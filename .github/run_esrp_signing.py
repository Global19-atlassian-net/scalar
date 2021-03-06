import json
import os
import glob
import pprint
import subprocess
import sys

esrp_tool = os.path.join("esrp", "tools", "EsrpClient.exe")

aad_id = os.environ['AZURE_AAD_ID'].strip()
workspace = os.environ['GITHUB_WORKSPACE'].strip()

source_root_location = os.path.join(workspace, "tosign")
destination_location = os.path.join(workspace)

scalar_files = glob.glob(os.path.join(source_root_location, "scalar-linux*.deb"))
azrepos_files = glob.glob(os.path.join(source_root_location, "scalar-azrepos-linux*.deb"))

print("Found files:")
pprint.pp(scalar_files)
pprint.pp(azrepos_files)

if len(scalar_files) < 1 or not scalar_files[0].endswith(".deb"):
	print("Error: cannot find scalar .deb to sign")
	exit(1)

if len(azrepos_files) < 1 or not azrepos_files[0].endswith(".deb"):
	print("Error: cannot find scalar-azrepos .deb to sign")
	exit(1)

scalar_to_sign = os.path.basename(scalar_files[0])
azrepos_to_sign = os.path.basename(azrepos_files[0])

auth_json = {
	"Version": "1.0.0",
	"AuthenticationType": "AAD_CERT",
	"TenantId": "72f988bf-86f1-41af-91ab-2d7cd011db47",
	"ClientId": aad_id,
	"AuthCert": {
		"SubjectName": f"CN={aad_id}.microsoft.com",
		"StoreLocation": "LocalMachine",
		"StoreName": "My",
	},
	"RequestSigningCert": {
		"SubjectName": f"CN={aad_id}",
		"StoreLocation": "LocalMachine",
		"StoreName": "My",
	}
}

input_json = {
	"Version": "1.0.0",
	"SignBatches": [
		{
			"SourceLocationType": "UNC",
			"SourceRootDirectory": source_root_location,
			"DestinationLocationType": "UNC",
			"DestinationRootDirectory": destination_location,
			"SignRequestFiles": [
				{
					"CustomerCorrelationId": "01A7F55F-6CDD-4123-B255-77E6F212CDAD",
					"SourceLocation": scalar_to_sign,
					"DestinationLocation": os.path.join("signed", scalar_to_sign),
				},
				{
					"CustomerCorrelationId": "01A7F55F-6CDD-4123-B255-77E6F212CDAD",
					"SourceLocation": azrepos_to_sign,
					"DestinationLocation": os.path.join("signed", azrepos_to_sign),
				}
			],
			"SigningInfo": {
				"Operations": [
					{
						"KeyCode": "CP-450779-Pgp",
						"OperationCode": "LinuxSign",
						"Parameters": {},
						"ToolName": "sign",
						"ToolVersion": "1.0",
					}
				]
			}
		}
	]
}

policy_json = {
	"Version": "1.0.0",
	"Intent": "production release",
	"ContentType": "Debian package",
}

configs = [
	("auth.json", auth_json),
	("input.json", input_json),
	("policy.json", policy_json),
]

for filename, data in configs:
	with open(filename, 'w') as fp:
		json.dump(data, fp)

# Run ESRP Client
esrp_out = "esrp_out.json"
result = subprocess.run(
	[esrp_tool, "sign",
	"-a", "auth.json",
	"-i", "input.json",
	"-p", "policy.json",
	"-o", esrp_out,
	"-l", "Verbose"],
	cwd=workspace)

if result.returncode != 0:
	print("Failed to run ESRPClient.exe")
	sys.exit(1)

if os.path.isfile(esrp_out):
	print("ESRP output json:")
	with open(esrp_out, 'r') as fp:
		pprint.pp(json.load(fp))

scalar_signed = os.path.join(destination_location, "signed", scalar_to_sign)
if os.path.isfile(scalar_signed):
	print(f"Success!\nSigned {scalar_signed}")

azrepos_to_sign = os.path.join(destination_location, "signed", azrepos_to_sign)
if os.path.isfile(azrepos_to_sign):
	print(f"Success!\nSigned {azrepos_to_sign}")
