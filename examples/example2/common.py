class Repository(dict):
    def add(self, item):
        self[item.id] = item

    def remove(self, item_id):
        del self[item_id]
