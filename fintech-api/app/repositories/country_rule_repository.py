"""
Repository for country rules CRUD operations
"""
from typing import Optional, List
from datetime import datetime
from app.core.database import get_database
from app.models.country_rule import CountryRuleInDB
from app.models.credit_request import Country
from bson import ObjectId


class CountryRuleRepository:
    def __init__(self):
        self.collection_name = "country_rules"

    async def create(self, country_rule: CountryRuleInDB) -> CountryRuleInDB:
        """Create a new country rule"""
        db = get_database()
        country_rule_dict = country_rule.model_dump(by_alias=True, exclude={"id"})
        result = await db[self.collection_name].insert_one(country_rule_dict)
        country_rule.id = result.inserted_id
        return country_rule

    async def get_by_id(self, rule_id: str) -> Optional[CountryRuleInDB]:
        """Get country rule by ID"""
        db = get_database()
        rule_doc = await db[self.collection_name].find_one({"_id": ObjectId(rule_id)})
        if rule_doc:
            return CountryRuleInDB(**rule_doc)
        return None

    async def get_by_country(self, country: Country) -> Optional[CountryRuleInDB]:
        """Get country rule by country code"""
        db = get_database()
        rule_doc = await db[self.collection_name].find_one({
            "country": country.value if hasattr(country, 'value') else str(country),
            "is_active": True
        })
        if rule_doc:
            return CountryRuleInDB(**rule_doc)
        return None

    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[CountryRuleInDB]:
        """Get all country rules with pagination"""
        db = get_database()
        query = {}
        if is_active is not None:
            query["is_active"] = is_active
        
        cursor = db[self.collection_name].find(query).skip(skip).limit(limit).sort("country", 1)
        rules = []
        async for doc in cursor:
            rules.append(CountryRuleInDB(**doc))
        return rules

    async def update(self, rule_id: str, update_data: dict, updated_by: Optional[str] = None) -> Optional[CountryRuleInDB]:
        """Update a country rule"""
        db = get_database()
        update_data["updated_at"] = datetime.utcnow()
        if updated_by:
            update_data["updated_by"] = ObjectId(updated_by)
        
        result = await db[self.collection_name].update_one(
            {"_id": ObjectId(rule_id)},
            {"$set": update_data}
        )
        if result.modified_count > 0:
            return await self.get_by_id(rule_id)
        return None

    async def delete(self, rule_id: str) -> bool:
        """Delete a country rule (soft delete by setting is_active=False)"""
        db = get_database()
        result = await db[self.collection_name].update_one(
            {"_id": ObjectId(rule_id)},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0

    async def hard_delete(self, rule_id: str) -> bool:
        """Permanently delete a country rule"""
        db = get_database()
        result = await db[self.collection_name].delete_one({"_id": ObjectId(rule_id)})
        return result.deleted_count > 0

    async def count(self, is_active: Optional[bool] = None) -> int:
        """Count country rules"""
        db = get_database()
        query = {}
        if is_active is not None:
            query["is_active"] = is_active
        return await db[self.collection_name].count_documents(query)


country_rule_repository = CountryRuleRepository()
