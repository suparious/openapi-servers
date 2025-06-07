"""
Graph operations helper for direct Neo4j interactions
"""
from neo4j import AsyncGraphDatabase
from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class GraphOperations:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = AsyncGraphDatabase.driver(uri, auth=(user, password))
    
    async def close(self):
        await self.driver.close()
    
    async def create_node(self, name: str, node_type: str, summary: Optional[str] = None, 
                         group_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new node in the graph"""
        node_uuid = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        
        async with self.driver.session() as session:
            query = """
            CREATE (n:Entity {
                uuid: $uuid,
                name: $name,
                summary: $summary,
                group_id: $group_id,
                created_at: $created_at
            })
            SET n:$node_type
            RETURN n
            """
            
            # Neo4j doesn't allow parameterized labels, so we need to build the query differently
            query = f"""
            CREATE (n:`{node_type}` {{
                uuid: $uuid,
                name: $name,
                summary: $summary,
                group_id: $group_id,
                created_at: $created_at
            }})
            RETURN n
            """
            
            result = await session.run(
                query,
                uuid=node_uuid,
                name=name,
                summary=summary,
                group_id=group_id,
                created_at=created_at
            )
            
            record = await result.single()
            if record:
                node = record["n"]
                return {
                    "uuid": node["uuid"],
                    "name": node["name"],
                    "summary": node["summary"],
                    "group_id": node["group_id"],
                    "created_at": node["created_at"],
                    "type": node_type
                }
            raise Exception("Failed to create node")
    
    async def create_relationship(self, source_uuid: str, target_uuid: str, 
                                relationship_type: str, summary: Optional[str] = None,
                                group_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a relationship between two nodes"""
        rel_uuid = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        
        async with self.driver.session() as session:
            # Sanitize relationship type for Neo4j
            rel_type = relationship_type.upper().replace(" ", "_")
            
            query = f"""
            MATCH (source {{uuid: $source_uuid}})
            MATCH (target {{uuid: $target_uuid}})
            CREATE (source)-[r:`{rel_type}` {{
                uuid: $uuid,
                summary: $summary,
                group_id: $group_id,
                created_at: $created_at
            }}]->(target)
            RETURN source, r, target
            """
            
            result = await session.run(
                query,
                source_uuid=source_uuid,
                target_uuid=target_uuid,
                uuid=rel_uuid,
                summary=summary,
                group_id=group_id,
                created_at=created_at
            )
            
            record = await result.single()
            if record:
                return {
                    "uuid": rel_uuid,
                    "source_uuid": source_uuid,
                    "target_uuid": target_uuid,
                    "type": relationship_type,
                    "summary": summary,
                    "group_id": group_id,
                    "created_at": created_at
                }
            raise Exception("Failed to create relationship - nodes may not exist")
    
    async def get_node_by_uuid(self, node_uuid: str) -> Optional[Dict[str, Any]]:
        """Get a node by its UUID"""
        async with self.driver.session() as session:
            query = """
            MATCH (n {uuid: $uuid})
            RETURN n, labels(n) as labels
            """
            
            result = await session.run(query, uuid=node_uuid)
            record = await result.single()
            
            if record:
                node = record["n"]
                labels = record["labels"]
                # Filter out 'Entity' label if present
                node_type = next((l for l in labels if l != "Entity"), labels[0] if labels else "Unknown")
                
                return {
                    "uuid": node.get("uuid"),
                    "name": node.get("name"),
                    "summary": node.get("summary"),
                    "group_id": node.get("group_id"),
                    "created_at": node.get("created_at"),
                    "type": node_type
                }
            return None
    
    async def update_node(self, node_uuid: str, name: Optional[str] = None, 
                         summary: Optional[str] = None) -> Dict[str, Any]:
        """Update a node's properties"""
        async with self.driver.session() as session:
            # Build SET clause dynamically
            set_clauses = []
            params = {"uuid": node_uuid}
            
            if name is not None:
                set_clauses.append("n.name = $name")
                params["name"] = name
            
            if summary is not None:
                set_clauses.append("n.summary = $summary")
                params["summary"] = summary
            
            if not set_clauses:
                # No updates requested
                node = await self.get_node_by_uuid(node_uuid)
                if node:
                    return node
                raise Exception("Node not found")
            
            set_clause = ", ".join(set_clauses)
            query = f"""
            MATCH (n {{uuid: $uuid}})
            SET {set_clause}
            RETURN n, labels(n) as labels
            """
            
            result = await session.run(query, **params)
            record = await result.single()
            
            if record:
                node = record["n"]
                labels = record["labels"]
                node_type = next((l for l in labels if l != "Entity"), labels[0] if labels else "Unknown")
                
                return {
                    "uuid": node.get("uuid"),
                    "name": node.get("name"),
                    "summary": node.get("summary"),
                    "group_id": node.get("group_id"),
                    "created_at": node.get("created_at"),
                    "type": node_type
                }
            raise Exception("Node not found")
    
    async def delete_node(self, node_uuid: str) -> bool:
        """Delete a node and all its relationships"""
        async with self.driver.session() as session:
            query = """
            MATCH (n {uuid: $uuid})
            DETACH DELETE n
            RETURN count(n) as deleted_count
            """
            
            result = await session.run(query, uuid=node_uuid)
            record = await result.single()
            
            if record and record["deleted_count"] > 0:
                return True
            return False
    
    async def get_graph_stats(self) -> Dict[str, Any]:
        """Get statistics about the graph"""
        async with self.driver.session() as session:
            # Get node count and types
            node_query = """
            MATCH (n)
            RETURN count(n) as total_nodes, collect(DISTINCT labels(n)) as node_labels
            """
            
            node_result = await session.run(node_query)
            node_record = await node_result.single()
            
            # Get relationship count and types
            rel_query = """
            MATCH ()-[r]->()
            RETURN count(r) as total_relationships, collect(DISTINCT type(r)) as rel_types
            """
            
            rel_result = await session.run(rel_query)
            rel_record = await rel_result.single()
            
            # Get episode count
            episode_query = """
            MATCH (e:Episode)
            RETURN count(e) as total_episodes
            """
            
            episode_result = await session.run(episode_query)
            episode_record = await episode_result.single()
            
            # Process node labels
            all_labels = []
            if node_record and node_record["node_labels"]:
                for label_list in node_record["node_labels"]:
                    all_labels.extend(label_list)
            unique_labels = list(set(all_labels))
            
            return {
                "total_nodes": node_record["total_nodes"] if node_record else 0,
                "total_relationships": rel_record["total_relationships"] if rel_record else 0,
                "total_episodes": episode_record["total_episodes"] if episode_record else 0,
                "node_types": unique_labels,
                "relationship_types": list(rel_record["rel_types"]) if rel_record and rel_record["rel_types"] else []
            }
