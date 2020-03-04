import yaml

def yaml_loader(filepath):
	"""Loads a yaml file"""
	with open(filepath, "r") as stream:
		data = yaml.safe_load(stream)
	return data

def yaml_dump(filepath, data):
	"""Dumps data to a yaml file"""
	with open(filepath, "w") as stream:
		yaml.dump(data, stream)

if __name__ == "__main__":
	filepath = "test.yaml"
	data = yaml_loader(filepath)
	sort_file = yaml.dump(data, \n,  sort_keys=True)
	print(sort_file)

	items = data.get('clients')
	for item_name, item_value in items.items():
		print (item_name, item_value)
