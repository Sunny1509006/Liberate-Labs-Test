import chromadb
from chromadb.config import Settings
from typing import Dict, List, Optional
import json
import hashlib
from datetime import datetime, timedelta

class DBManager:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./data")
        
        # Create collections if they don't exist
        self.competitors_collection = self.client.get_or_create_collection(
            name="competitors",
            metadata={"description": "Competitor analysis data"}
        )
        
        self.search_results_collection = self.client.get_or_create_collection(
            name="search_results",
            metadata={"description": "Google search results"}
        )

    def _generate_id(self, data: str) -> str:
        """Generate a unique ID for a document"""
        return hashlib.md5(data.encode()).hexdigest()

    def _add_timestamp(self, data: Dict) -> Dict:
        """Add timestamp to data for tracking freshness"""
        data['last_updated'] = datetime.utcnow().isoformat()
        return data

    async def get_competitor_data(self, competitor_identifier: str) -> Optional[Dict]:
        """Retrieve competitor data if it exists"""
        try:
            doc_id = self._generate_id(competitor_identifier)
            
            try:
                result = self.competitors_collection.get(
                    ids=[doc_id],
                    include=['documents', 'metadatas']
                )
            except Exception:
                return None
                
            if result and result['documents']:
                data = json.loads(result['documents'][0])
                
                # Check if data is older than 30 days
                last_updated = datetime.fromisoformat(data.get('last_updated', '2000-01-01'))
                days_old = (datetime.utcnow() - last_updated).days
                
                if days_old > 30:
                    # Delete old data
                    self.competitors_collection.delete(ids=[doc_id])
                    return None  # Return None to trigger fresh data collection
                    
                return data
            return None
        except Exception as e:
            print(f"Error retrieving competitor data: {str(e)}")
            return None

    async def store_competitor_data(self, competitor_data: Dict) -> bool:
        """Store competitor analysis data"""
        try:
            # Extract the identifier (website or name) from the nested structure
            identifier = competitor_data.get('company_info', {}).get('website', '') or \
                        competitor_data.get('company_info', {}).get('name', '')
            
            if not identifier:
                raise ValueError("No valid identifier (website or name) found in competitor data")
            
            doc_id = self._generate_id(identifier)
            
            # Add timestamp and prepare metadata
            data_to_store = self._add_timestamp(competitor_data.copy())
            metadata = {
                "name": competitor_data.get('company_info', {}).get('name', ''),
                "website": competitor_data.get('company_info', {}).get('website', ''),
                "stored_at": datetime.utcnow().isoformat()
            }
            
            try:
                # Check if document exists
                self.competitors_collection.get(ids=[doc_id])
                # Update existing data
                self.competitors_collection.update(
                    ids=[doc_id],
                    documents=[json.dumps(data_to_store)],
                    metadatas=[metadata]
                )
            except Exception:
                # Store new data
                self.competitors_collection.add(
                    documents=[json.dumps(data_to_store)],
                    metadatas=[metadata],
                    ids=[doc_id]
                )
            return True
        except Exception as e:
            print(f"Error storing competitor data: {str(e)}")
            return False

    async def get_search_results(self, query: str) -> Optional[List[Dict]]:
        """Retrieve search results for a query if they exist"""
        try:
            doc_id = self._generate_id(query)
            
            try:
                result = self.search_results_collection.get(
                    ids=[doc_id],
                    include=['documents', 'metadatas']
                )
            except Exception:
                return None
                
            if result and result['documents']:
                data = json.loads(result['documents'][0])
                
                # Check if data is older than 7 days
                last_updated = datetime.fromisoformat(data[0].get('last_updated', '2000-01-01'))
                days_old = (datetime.utcnow() - last_updated).days
                
                if days_old > 7:
                    # Delete old data
                    self.search_results_collection.delete(ids=[doc_id])
                    return None  # Return None to trigger fresh data collection
                    
                return data
            return None
        except Exception as e:
            print(f"Error retrieving search results: {str(e)}")
            return None

    async def store_search_results(self, query: str, results: List[Dict]) -> bool:
        """Store search results"""
        try:
            doc_id = self._generate_id(query)
            
            # Add timestamp to each result
            results_with_timestamp = [self._add_timestamp(result.copy()) for result in results]
            metadata = {
                "query": query,
                "stored_at": datetime.utcnow().isoformat(),
                "result_count": len(results)
            }
            
            try:
                # Check if document exists
                self.search_results_collection.get(ids=[doc_id])
                # Update existing data
                self.search_results_collection.update(
                    ids=[doc_id],
                    documents=[json.dumps(results_with_timestamp)],
                    metadatas=[metadata]
                )
            except Exception:
                # Store new results
                self.search_results_collection.add(
                    documents=[json.dumps(results_with_timestamp)],
                    metadatas=[metadata],
                    ids=[doc_id]
                )
            return True
        except Exception as e:
            print(f"Error storing search results: {str(e)}")
            return False

    async def clear_old_data(self) -> bool:
        """Clear data older than the retention period"""
        try:
            # Get all documents
            competitors = self.competitors_collection.get()
            search_results = self.search_results_collection.get()
            
            # Clear old competitor data (older than 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            for idx, metadata in enumerate(competitors.get('metadatas', [])):
                stored_at = datetime.fromisoformat(metadata.get('stored_at', '2000-01-01'))
                if stored_at < thirty_days_ago:
                    self.competitors_collection.delete(ids=[competitors['ids'][idx]])
            
            # Clear old search results (older than 7 days)
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            for idx, metadata in enumerate(search_results.get('metadatas', [])):
                stored_at = datetime.fromisoformat(metadata.get('stored_at', '2000-01-01'))
                if stored_at < seven_days_ago:
                    self.search_results_collection.delete(ids=[search_results['ids'][idx]])
            
            return True
        except Exception as e:
            print(f"Error clearing old data: {str(e)}")
            return False