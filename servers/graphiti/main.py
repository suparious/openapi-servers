from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv
from graphiti_core import Graphiti
from graphiti_core.llm_client import LLMConfig
from graphiti_core.nodes import EpisodeType
from graph_operations import GraphOperations
import asyncio
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Graphiti Knowledge Graph API",
    version="0.1.0",
    description="A temporal knowledge graph API for AI agents with episodic memory capabilities",
)

# CORS configuration
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Graphiti instance
graphiti_instance = None
graph_ops = None

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

if not NEO4J_PASSWORD:
    raise ValueError("NEO4J_PASSWORD environment variable is required")

# LLM Configuration
llm_config = LLMConfig(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o-mini",
    base_url=os.getenv("OPENAI_BASE_URL"),
)

# Support for alternative LLM providers
if os.getenv("ANTHROPIC_API_KEY"):
    llm_config = LLMConfig(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        model="claude-3-5-sonnet-20241022",
    )
elif os.getenv("GROQ_API_KEY"):
    llm_config = LLMConfig(
        api_key=os.getenv("GROQ_API_KEY"),
        model="llama-3.3-70b-versatile",
    )
elif os.getenv("GOOGLE_API_KEY"):
    llm_config = LLMConfig(
        api_key=os.getenv("GOOGLE_API_KEY"),
        model="gemini-2.0-flash",
    )

# ------------------------------------------------------------------------------
# Pydantic Models
# ------------------------------------------------------------------------------

class AddEpisodeRequest(BaseModel):
    content: str = Field(..., description="The content of the episode to add")
    source: str = Field(..., description="Description of the episode source")
    name: Optional[str] = Field(None, description="Optional name for the episode")
    episode_type: Optional[str] = Field("message", description="Type of episode (message, event, etc.)")
    reference_time: Optional[str] = Field(None, description="ISO format timestamp for the episode")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the episode")

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query string")
    limit: Optional[int] = Field(10, description="Maximum number of results to return")
    center_node_uuid: Optional[str] = Field(None, description="UUID of node to center search around")
    group_ids: Optional[List[str]] = Field(None, description="List of group IDs to filter results")
    num_hops: Optional[int] = Field(2, description="Number of hops for graph traversal")

class AddNodeRequest(BaseModel):
    name: str = Field(..., description="Name of the node")
    node_type: str = Field(..., description="Type of the node (e.g., person, place, concept)")
    summary: Optional[str] = Field(None, description="Summary description of the node")
    group_id: Optional[str] = Field(None, description="Group ID for the node")

class AddRelationshipRequest(BaseModel):
    source_node_uuid: str = Field(..., description="UUID of the source node")
    target_node_uuid: str = Field(..., description="UUID of the target node")
    relationship_type: str = Field(..., description="Type of relationship")
    summary: Optional[str] = Field(None, description="Summary of the relationship")
    group_id: Optional[str] = Field(None, description="Group ID for the relationship")

class GetNodeRequest(BaseModel):
    uuid: str = Field(..., description="UUID of the node to retrieve")

class UpdateNodeRequest(BaseModel):
    uuid: str = Field(..., description="UUID of the node to update")
    name: Optional[str] = Field(None, description="New name for the node")
    summary: Optional[str] = Field(None, description="New summary for the node")

class DeleteNodeRequest(BaseModel):
    uuid: str = Field(..., description="UUID of the node to delete")

# ------------------------------------------------------------------------------
# Startup/Shutdown Events
# ------------------------------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    """Initialize Graphiti connection and build indices"""
    global graphiti_instance, graph_ops
    try:
        logger.info(f"Connecting to Neo4j at {NEO4J_URI}")
        graphiti_instance = Graphiti(
            uri=NEO4J_URI,
            user=NEO4J_USER,
            password=NEO4J_PASSWORD,
            llm_config=llm_config,
        )
        
        # Initialize graph operations helper
        graph_ops = GraphOperations(
            uri=NEO4J_URI,
            user=NEO4J_USER,
            password=NEO4J_PASSWORD,
        )
        
        # Build indices and constraints
        await graphiti_instance.build_indices_and_constraints()
        logger.info("Successfully connected to Graphiti and built indices")
    except Exception as e:
        logger.error(f"Failed to initialize Graphiti: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Close Graphiti connection"""
    global graphiti_instance, graph_ops
    if graphiti_instance:
        await graphiti_instance.close()
        logger.info("Closed Graphiti connection")
    if graph_ops:
        await graph_ops.close()
        logger.info("Closed graph operations connection")

# ------------------------------------------------------------------------------
# API Routes
# ------------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    """Check health status of the API and Neo4j connection"""
    try:
        # Test Neo4j connection
        if graphiti_instance:
            # Simple query to test connection
            await graphiti_instance.search("test", limit=1)
            return {"status": "healthy", "neo4j": "connected"}
        else:
            return {"status": "unhealthy", "neo4j": "disconnected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")

@app.post("/episodes/add")
async def add_episode(request: AddEpisodeRequest = Body(...)):
    """Add a new episode to the knowledge graph"""
    try:
        episode_type = EpisodeType[request.episode_type.upper()] if request.episode_type else EpisodeType.MESSAGE
        
        result = await graphiti_instance.add_episode(
            name=request.name,
            episode_body=request.content,
            source_description=request.source,
            episode_type=episode_type,
            reference_time=request.reference_time,
            metadata=request.metadata,
        )
        
        return {
            "success": True,
            "message": "Episode added successfully",
            "episode_uuid": str(result.episode.uuid) if result and result.episode else None,
        }
    except Exception as e:
        logger.error(f"Failed to add episode: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add episode: {str(e)}")

@app.post("/search")
async def search(request: SearchRequest = Body(...)):
    """Search the knowledge graph"""
    try:
        results = await graphiti_instance.search(
            query=request.query,
            limit=request.limit,
            center_node_uuid=request.center_node_uuid,
            group_ids=request.group_ids,
            num_hops=request.num_hops,
        )
        
        # Convert results to JSON-serializable format
        formatted_results = []
        for result in results:
            formatted_results.append({
                "uuid": str(result.uuid),
                "name": result.name,
                "node_type": result.labels[0] if result.labels else None,
                "summary": result.summary if hasattr(result, 'summary') else None,
                "score": getattr(result, 'score', None),
            })
        
        return {
            "success": True,
            "query": request.query,
            "results": formatted_results,
            "count": len(formatted_results),
        }
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/nodes/add")
async def add_node(request: AddNodeRequest = Body(...)):
    """Add a new node to the knowledge graph"""
    try:
        if not graph_ops:
            raise HTTPException(status_code=503, detail="Graph operations not initialized")
        
        node = await graph_ops.create_node(
            name=request.name,
            node_type=request.node_type,
            summary=request.summary,
            group_id=request.group_id,
        )
        
        return {
            "success": True,
            "message": "Node created successfully",
            "node": node,
        }
    except Exception as e:
        logger.error(f"Failed to add node: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add node: {str(e)}")

@app.post("/relationships/add")
async def add_relationship(request: AddRelationshipRequest = Body(...)):
    """Add a new relationship between nodes"""
    try:
        if not graph_ops:
            raise HTTPException(status_code=503, detail="Graph operations not initialized")
        
        relationship = await graph_ops.create_relationship(
            source_uuid=request.source_node_uuid,
            target_uuid=request.target_node_uuid,
            relationship_type=request.relationship_type,
            summary=request.summary,
            group_id=request.group_id,
        )
        
        return {
            "success": True,
            "message": "Relationship created successfully",
            "relationship": relationship,
        }
    except Exception as e:
        logger.error(f"Failed to add relationship: {str(e)}")
        if "nodes may not exist" in str(e):
            raise HTTPException(status_code=404, detail="One or both nodes not found")
        raise HTTPException(status_code=500, detail=f"Failed to add relationship: {str(e)}")

@app.get("/nodes/{uuid}")
async def get_node(uuid: str):
    """Get a specific node by UUID"""
    try:
        if not graph_ops:
            raise HTTPException(status_code=503, detail="Graph operations not initialized")
        
        node = await graph_ops.get_node_by_uuid(uuid)
        
        if not node:
            raise HTTPException(status_code=404, detail="Node not found")
        
        return {
            "success": True,
            "node": node,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get node: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get node: {str(e)}")

@app.put("/nodes/update")
async def update_node(request: UpdateNodeRequest = Body(...)):
    """Update an existing node"""
    try:
        if not graph_ops:
            raise HTTPException(status_code=503, detail="Graph operations not initialized")
        
        node = await graph_ops.update_node(
            node_uuid=request.uuid,
            name=request.name,
            summary=request.summary,
        )
        
        return {
            "success": True,
            "message": "Node updated successfully",
            "node": node,
        }
    except Exception as e:
        logger.error(f"Failed to update node: {str(e)}")
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Node not found")
        raise HTTPException(status_code=500, detail=f"Failed to update node: {str(e)}")

@app.delete("/nodes/delete")
async def delete_node(request: DeleteNodeRequest = Body(...)):
    """Delete a node from the knowledge graph"""
    try:
        if not graph_ops:
            raise HTTPException(status_code=503, detail="Graph operations not initialized")
        
        deleted = await graph_ops.delete_node(request.uuid)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Node not found")
        
        return {
            "success": True,
            "message": "Node deleted successfully",
            "deleted_uuid": request.uuid,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete node: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete node: {str(e)}")

@app.get("/graph/stats")
async def get_graph_stats():
    """Get statistics about the knowledge graph"""
    try:
        if not graph_ops:
            raise HTTPException(status_code=503, detail="Graph operations not initialized")
        
        stats = await graph_ops.get_graph_stats()
        
        return {
            "success": True,
            "stats": stats,
        }
    except Exception as e:
        logger.error(f"Failed to get graph stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get graph stats: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Graphiti Knowledge Graph API",
        "version": "0.1.0",
        "description": "Temporal knowledge graph for AI agents",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc",
            "episodes": {
                "add": "POST /episodes/add",
            },
            "search": "POST /search",
            "nodes": {
                "add": "POST /nodes/add",
                "get": "GET /nodes/{uuid}",
                "update": "PUT /nodes/update",
                "delete": "DELETE /nodes/delete",
            },
            "relationships": {
                "add": "POST /relationships/add",
            },
            "graph": {
                "stats": "GET /graph/stats",
            },
        },
    }
