from app.models import Item, ItemCreate

class ItemStore:
    """In-memory store for Item objects."""
    def __init__(self):
        #key:UUID, value:Item
        self._items: dict[str, Item] = {}
    
    def create_item(self, item_create:ItemCreate):
        """Create and persist a new Item from the given ItemCreate Payload."""
        data = item_create.model_dump() if hasattr(item_create, "model_dump") else item_create.dict()
        item = Item(**data)
        self._items[str(item.id)] = item
        return item
    
    def get_item(self, item_id: str) -> Item | None:
        """Get Item with Item ID"""
        return self._items.get(str(item_id))
    
    def list_items(self) -> list[Item]:
        """List the created items"""
        return list(self._items.values())
    
    def delete_item(self,item_id:str):
        """Delete Item"""
        if item_id in self._items:
            del self._items[item_id]
            return True
        return False
#Global instance 
store = ItemStore()