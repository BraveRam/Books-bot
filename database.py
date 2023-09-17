import dns.resolver
dns.resolver.default_resolver=dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers=['8.8.8.8']
import pymongo
from pymongo import MongoClient
import helpers.config as config

class Database:
	def __init__(self):
		self.client = MongoClient(config.MONGO_DB_URL)
		self.db = self.client["Booksdb"]
		self.collection = self.db["books"]	
	
	def find_user(self, user_id):
		user = self.collection.find_one({"user_id": int(user_id)})		
		if user:
			return True
		return False
	
	def save_user(self, user_id, premium=False, total_books=0, banned=False, accepted_terms=False):
		return self.collection.insert_one({"user_id": int(user_id), "premium": premium, "total_books": total_books, "banned": banned, "accepted_terms": accepted_terms})
	
	def inc_total_books(self, user_id):
		return self.collection.update_one({"user_id": user_id}, {"$inc": {"total_books": 1}})
	
	def accepted_tos(self, user_id):
		return self.collection.update_one({"user_id": user_id}, {"$set": {"accepted_terms": True}})
	
	def check_accept(self, user_id):
		user = self.collection.find_one({"user_id": int(user_id)})		
		if user["accepted_terms"] == True:
			return True
		return False
							
	def ban_user(self, user_id):
		return self.collection.update_one({"user_id": user_id}, {"$set": {"banned": True}})
	
	def unban_user(self, user_id):
		return self.collection.update_one({"user_id": user_id}, {"$set": {"banned": False}})
	
	def set_premium(self, user_id):
		return self.collection.update_one({"user_id": user_id}, {"$set": {"premium": True, "banned": False}})
	
	def unset_premium(self, user_id):
		return self.collection.update_one({"user_id": user_id}, {"$set": {"premium": False}})
	
	def is_admin(self, user_id):
		if not user_id in config.ADMINS_ID:
			return False		
		return True
	
	def get_stats(self):
		return len(list(self.collection.find({})))
		 
