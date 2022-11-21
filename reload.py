import os
from pathlib import Path

import docker
import requests
from slugify import slugify


class SwarmServiceReloader:
	"""
	Reloads desired target service with pulling "latest" image before
	"""

	last_value_file_path = ""
	client = None
	watched_url = None
	target_services = None

	def __init__(self):
		self.client = docker.from_env()
		self.watched_url = os.getenv("SWARM_SERVICE_RELOADER_WATCHED_URL")
		self.target_services = os.getenv("SWARM_SERVICE_RELOADER_TARGET_SERVICES").split(",")
		self.last_value_file_path = f"/tmp/{slugify(self.watched_url)}.txt"

	def run(self):
		force_update = False
		last_value = self.get_last_value()
		latest_value = self.get_latest_value()

		if not latest_value:
			print("Can't compare values. Exit.")
			return

		if last_value != latest_value or not last_value:
			self.reload_services()

		self.save_last_value(last_value=latest_value)

	def get_last_value(self):
		last_value = ""

		try:
			with open(self.last_value_file_path, 'r+') as last_file:
				try:
					last_value = last_file.read()
				except Exception as e:
					print(f"Reading last value failed: {e}")
		except FileNotFoundError:
			print("Last value file does not exist")

		return last_value

	def save_last_value(self, last_value: str):
		with open(self.last_value_file_path, 'w') as last_file:
			last_file.write(last_value)
			last_file.flush()
			print("Last value has benn updated.")

	def get_latest_value(self):
		response = requests.get(self.watched_url)

		if response.ok:

			print(f"Downloaded latest value {response.text}.")
			return response.text
		else:
			print(f"Reading latest value from {self.watched_url} failed.")
			return ""

	def reload_services(self):
		for s in self.client.services.list():
			if s.name in self.target_services:
				print(f"Found service id {s.id} for service {s.name}")

				full_img_path = s.attrs['Spec']['TaskTemplate']['ContainerSpec']['Image']
				img_path, img_tag = full_img_path.split("@")[0].split(":")
				if img_tag not in ['testing', 'develop']:
					img_tag = 'latest'

				print(f"Identifield image path: {img_path} and image tag: {img_tag}. Pulling image.")
				self.client.images.pull(img_path, tag=img_tag)

				s.update(force_update=True, fetch_current_spec=True, image=f"{img_path}:{img_tag}")
				print(f"Service {s.name} updated.")


if __name__ == '__main__':
	reloader = SwarmServiceReloader()
	reloader.run()
