#!/usr/local/bin/python3

# This tool will take an an artifact from commandline and grab IoC information such as exif and hashes and print them

# It can also be imported like a library to be used by other tools. 
# If used as a library, the items won't be printed to the console, as this is done in the Main function

import subprocess
import sys
from os.path import isdir, join, exists, splitext
from os import listdir
from re import findall, MULTILINE
from pathlib import PurePath
from xml.etree import ElementTree
from collections import defaultdict

# These shouldn't change that much, but possibly will from system to system. If so, set them here:
msbuildPath = '/usr/local/bin/msbuild'
cscPath = '/usr/local/bin/csc'


##### Compiler Functions #####

def msbuildCSharp(file, platform="x64", config="Release", target="Rebuild"):
	flags = [file, "/t:{}".format(target), "/p:Configuration={},Platform={}".format(config, platform)]
	output = subprocess.run([msbuildPath] + flags, capture_output=True)
	return output.stdout.decode()


def cscCSharp(file, platform="x64", target="winexe"):
	flags = [file, "/t:{}".format(target), "/platform:{}".format(platform)]
	output = subprocess.run([cscPath] + flags, capture_output=True)
	return output.stdout.decode()

########## Dynamic Functions ##########

def _dynamicallyDetermine(
	identifier: str, 
	func_name: str, 
	directory_id: str = 'Directory', 
	sln_id: str = 'Sln', 
	csproj_id: str = 'CsProj'
):
	"""A private function that is used to dynamically determine which corresponding function run based off of whether 
	the input is a directory, a solution file, or a csproj file.

	Args:
		identifier (str): The input which identifies a directory, sln file, or csproj file.
		func_name (str): The function name to dynamically find the three corresponding functions from.
		directory_id (str, optional): The ID to add to the func_name to find the directory function. 
			Defaults to 'Directory'.
		sln_id (str, optional): The ID to add to the func_name to find the solution function. Defaults to 'Sln'.
		csproj_id (str, optional): The ID to add to the func_name to find the csproj function. Defaults to 'CsProj'.

	Returns:
		Any: The result from the dynamically invoked function.
	"""
	directory_func = file_locals.get(func_name + directory_id)
	sln_func = file_locals.get(func_name + sln_id)
	csproj_func = file_locals.get(func_name + csproj_id)

	# If is directory
	if isdir(identifier):
		if directory_func:
			return directory_func(identifier)
		else:
			print(f"[-] Directory Function: {func_name + directory_id} not found.")
	
	_, extension = splitext(identifier)
	# If is .sln
	if extension == '.sln':
		if sln_func:
			return sln_func(identifier)
		else:
			print(f"[-] Solution Function: {func_name + sln_id} not found.")

	# If is .csproj
	elif extension == '.csproj':
		if csproj_func:
			return csproj_func(identifier)
		else:
			print(f"[-] CsProj Function: {func_name + csproj_id} not found.")

def _dynamicDirectory(directory: str, func_name: str, sln_id: str = 'Sln') -> list:
	"""Dynamically invokes a function for parsing a directory for a sln file.

	Args:
		directory (str): The directory containing a sln file.
		func_name (str): The function name to run the solution function on.
		sln_id (str, optional): The ID to append to the function name to find the solution function. Defaults to 'Sln'.

	Returns:
		list: A list of all the results from every solution file.
	"""
	results = list()
	sln_func = file_locals.get(func_name + sln_id)
	if sln_func:
		sln_files = parseDirectory(directory)
		for sln_file in sln_files:
			results += sln_func(sln_file)

	return results


def _dynamicSln(sln_file: str, func_name: str, csproj_id: str = 'CsProj') -> list:
	"""Dynamically invokes a function for parsing a sln file.

	Args:
		sln_file (str): The solution file to parse.
		func_name (str): The name of the function to dynamically run.
		csproj_id (str, optional): The ID to append to the function name to find the csproj function. Defaults to 'CsProj'.

	Returns:
		list: A list of all the results from every csproj file in this sln file.
	"""
	results = list()
	csproj_func = file_locals.get(func_name + csproj_id)
	if csproj_func:
		csproj_files = parseSln(sln_file)
		for csproj_file in csproj_files:
			result = csproj_func(csproj_file)
			results.append(result)

	return results

########## Helper Functions ##########

def getCsProjTags(csproj_file: str, tag: str):
	"""Gets a list of tags from a csproj file

	Args:
		csproj_file (str): The file to extract tags from.
		tag (str): The tags to search the csproj file for.

	Returns:
		Iterator: Iterator of element tree objects
	"""
	try:
		tree = ElementTree.parse(csproj_file)
		root = tree.getroot()
		# All tags have a header in front of them for whatever reason so we need to add that
		tagHeader = root.tag.replace('Project', '')
		realTag = tagHeader + tag
		return root.iter(realTag)
	except FileNotFoundError:
		# Return empty generator
		return iter(())


def parseDirectory(directory: str) -> list:
	"""Parse a directory and return the paths of all .sln files.

	Args:
		directory (str): The directory to parse.

	Returns:
		list: The list of parsed out sln files.
	"""
	paths = list()
	if isdir(directory):
		files = listdir(directory)
		for file in files:
			if '.sln' in file:
				full_path = join(directory, file)
				paths.append(full_path)

	return paths


def parseSln(sln_file: str) -> list:
	"""Parse a solution file for all csproj files.

	Args:
		sln_file (str): The path to the sln file.

	Returns:
		list: The list of parsed csproj files.
	"""
	# Parse sln file for csproj
	projs = list()
	try:
		with open(sln_file, 'rt') as read_file:
			contents = read_file.read()

		csproj_regex = r'^Project\("{.*?}"\) = ".*?", "(.*?)", "{.*?}"$'
		matches = findall(csproj_regex, contents, MULTILINE)
		if matches:
			pure_path = PurePath(sln_file)
			# Remove the filename to get the path
			pure_parent = PurePath(*pure_path.parts[:-1])
			parent = str(pure_parent)

			for match in matches:
				if '.csproj' in match:
					# Sln file uses backslash, we need to convert this to regular slash
					replaced = match.replace('\\', '/')
					full_path = join(parent, replaced)
					projs.append(full_path)
	except FileNotFoundError:
		pass

	return projs


def parseConfiguration(condition: str) -> tuple:
	"""Extract the config and platform from the condition string.

	Args:
		condition (str): The string from the csproj file.

	Returns:
		tuple: The config and the platform.
	"""
	condition = condition.strip()
	config_platform_regex = r"^\'\$\(Configuration\)\|\$\(Platform\)' == '(.*?)\|(.*?)'$"
	matches = findall(config_platform_regex, condition, MULTILINE)
	if matches:
		for match in matches:
			config, platform = match
			return config, platform

	return tuple()


def extractConfigPlatform(the_dict: dict, config: str, platform: str) -> str:
	"""Extracts information for a config and platform from a dictionary.

	Args:
		the_dict (dict): The dict to parse information from.
		config (str): The config to fetch from the dict.
		platform (str): The platform to fetch from the dict.

	Returns:
		str: The found information.
	"""
	this_config = the_dict.get(config)
	if this_config:
		return this_config.get(platform)

########## CsProj Functions ##########

def getOutputNameCsProj(csproj_file: str) -> str:
	"""Get the output exe/dll name.

	Args:
		csproj_file (str): The path to the csproj file.

	Returns:
		str: The output exe/dll name.
	"""
	outputType = getOutputTypeCsProj(csproj_file)
	names = getCsProjTags(csproj_file, "AssemblyName")
	for name in names:
		output = name.text
		if outputType == 'Exe' or outputType == 'WinExe':
			output += '.exe'
		elif outputType == 'Library':
			output += '.dll'

		return output


def getOutputTypeCsProj(csproj_file: str) -> str:
	"""Gets the output type (Exe, WinExe, or Library) of the project.

	Args:
		csproj_file (str): The path to the csproj file.

	Returns:
		str: The output type.
	"""
	outputTypes = getCsProjTags(csproj_file, "OutputType")
	for outputType in outputTypes:
		return outputType.text


def getDebugTypeCsProj(csproj_file: str) -> dict:
	"""The debug type (what debug information is included in the exe).

	Args:
		csproj_file (str): The path to the csproj file.

	Returns:
		dict: A dict containing a dict mapping the config and platform with the debug type used.
	"""
	configuration_platform_debug_dict = defaultdict(dict)
	try:
		tree = ElementTree.parse(csproj_file)
		root = tree.getroot()
		tagHeader = root.tag.replace('Project', '')
		propertyGroupTag = tagHeader + 'PropertyGroup'
		propertyGroups = tree.findall(propertyGroupTag)
		for propertyGroup in propertyGroups:
			condition = propertyGroup.attrib.get('Condition')
			if condition:
				config, platform = parseConfiguration(condition)
				debugTypeTag = tagHeader + 'DebugType'
				debugTypes = propertyGroup.findall(debugTypeTag)
				for debugType in debugTypes:
					platform_debug_dict = configuration_platform_debug_dict[config]
					platform_debug_dict[platform] = debugType.text
		return dict(configuration_platform_debug_dict)

	except FileNotFoundError:
		return dict()


def getConfigurationsCsProj(csproj_file: str) -> dict:
	"""Gets the configuration options from the csproj file.

	Args:
		csproj_file (str): The path to the csproj file.

	Returns:
		dict: A dict containing the available config and platform obtions.
	"""
	configurations = getCsProjTags(csproj_file, "PropertyGroup")
	config_platforms = defaultdict(set)
	for config in configurations:
		condition = config.attrib.get('Condition')
		if condition:
			config, platform = parseConfiguration(condition)
			if config and platform:
				config_set = config_platforms[config]
				config_set.add(platform)
	
	return dict(config_platforms)

########## General Functions ##########

def getOutputName(identifier: str):
	"""Get the output name of the exe/dll.

	Args:
		identifier (str): The directory or sln file or csproj file to parse the output names from.

	Returns:
		Any: The output names.
	"""
	return _dynamicallyDetermine(identifier, 'getOutputName')


def getOutputType(identifier: str):
	"""Get the output type (Exe, WinExe or Library)

	Args:
		identifier (str): The directory or sln file or csproj file to parse the output names from.

	Returns:
		Any: The output types.
	"""
	return _dynamicallyDetermine(identifier, 'getOutputType')


def getDebugType(identifier: str):
	"""Gets the debug information for the project based off of the configurations.

	Args:
		identifier (str): The directory or sln file or csproj file to parse the output names from.

	Returns:
		Any: The debug information.
	"""
	return _dynamicallyDetermine(identifier, 'getDebugType')


def getConfigurations(identifier: str):
	"""Gets the configuration information for the project.

	Args:
		identifier (str): The directory or sln file or csproj file to parse the output names from.

	Returns:
		Any: The configurations.
	"""
	return _dynamicallyDetermine(identifier, 'getConfigurations')

########## Directory Functions ##########

def getOutputNameDirectory(directory: str) -> list:
	"""Gets the output name for a directory.

	Args:
		directory (str): The path to the directory containing at least one .sln file.

	Returns:
		list: The list of output names for this directory.
	"""
	return _dynamicDirectory(directory, 'getOutputName')


def getOutputTypeDirectory(directory: str) -> list:
	"""Gets the output type for a directory.

	Args:
		directory (str): The path to the directory containing at least one .sln file.

	Returns:
		list: The list of output types for this directory.
	"""
	return _dynamicDirectory(directory, 'getOutputType')


def getDebugTypeDirectory(directory: str) -> dict:
	"""Gets the debug information for a directory.

	Args:
		directory (str): The path to the directory containing at least one .sln file.

	Returns:
		dict: A dict containing the config information and the debug type for those configs.
	"""
	results = dict()
	sln_files = parseDirectory(directory)
	for sln_file in sln_files:
		results[sln_file] = getDebugTypeSln(sln_file)

	return results


def getConfigurationsDirectory(directory: str) -> dict:
	"""Gets the configurations for a directory.

	Args:
		directory (str): The path to the directory containing at least one .sln file.

	Returns:
		dict: A dict containing the config and platform information.
	"""
	results = dict()
	sln_files = parseDirectory(directory)
	for sln_file in sln_files:
		results[sln_file] = getConfigurationsSln(sln_file)

	return results

########## Solution Functions ##########

def getOutputNameSln(solution_file: str) -> list:
	"""Gets the output name of projects in this solution.

	Args:
		solution_file (str): The path to the sln file.

	Returns:
		list: A list of the output names for all projects in this solution file.
	"""
	return _dynamicSln(solution_file, 'getOutputName')


def getOutputTypeSln(sln_file: str) -> list:
	"""Gets the output type of projects in this solution.

	Args:
		sln_file (str): The path to the sln file.

	Returns:
		list: A list of the output types for all projects in this solution file.
	"""
	return _dynamicSln(sln_file, 'getOutputType')


def getDebugTypeSln(sln_file: str) -> dict:
	"""Gets the debug type for the projects.

	Args:
		sln_file (str): The path to the sln file.

	Returns:
		dict: A dict containing config and platform and debug type information.
	"""
	debug_types = dict()
	csproj_files = parseSln(sln_file)
	for csproj_file in csproj_files:
		debug_types[csproj_file] = getDebugTypeCsProj(csproj_file)

	return debug_types


def getConfigurationsSln(sln_file: str) -> dict:
	"""Gets configuration information for all projects in a solution.

	Args:
		sln_file (str): The path to the sln file.

	Returns:
		dict: A dict containing config and platform information.
	"""
	configurations = dict()
	csproj_files = parseSln(sln_file)
	for csproj_file in csproj_files:
		configurations[csproj_file] = getConfigurationsCsProj(csproj_file)

	return configurations

##### Main ########

def parseArguments():
	parser = ArgumentParser()

	parser.add_argument("-l", "--language", default="c#", 
		help="the language to compile. Currently supported: [C#,]")
	parser.add_argument("file", help="the solution, project, or source-code file to compile")

	args = parser.parse_args()
	return args


def main():
	pass


# This code is important so that the dynamic functions can find the defined functions (their locals would only return 
# functions declared within the function rather than the whole file)
file_locals = locals()

if __name__ == '__main__':
	# There are some imports which aren't used when this is a library, so they are imported here instead
	from argparse import ArgumentParser
	main()
