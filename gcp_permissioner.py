import argparse
import requests
import concurrent.futures
import os
import json
from tqdm import tqdm

# Resources dictionary
RESOURCE_APIS = json.load(open("resources.json", "r"))

def fetch_resource(name, api_config, project_id, access_token, output_dir):
    url = api_config['url'].format(project=project_id)
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        items = data.get(api_config['key'], {})

        # Count the resource instances
        count = len(items) if isinstance(items, list) else len(items.keys())

        # Save to file
        if count > 0:
            file_path = os.path.join(output_dir, f"{name}.json")
            with open(file_path, 'w') as f:
                json.dump(items, f, indent=2)

        return (name, count)
    except requests.exceptions.RequestException as e:
        return (name, 'error')


def main(project_id, access_token, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    summary_path = os.path.join(output_dir, "summary.txt")

    with open(summary_path, 'w') as summary:
        summary.write(f"Google Cloud Resource Access Summary for project: {project_id}\n")
        summary.write("------------------------------------------------------------\n")

    print(f"\n🔍 Scanning resources for project: {project_id}\n")

    progress = tqdm(total=len(RESOURCE_APIS), desc="Auditing access", ncols=100)
    accessible_resources = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(fetch_resource, name, api, project_id, access_token, output_dir): name
            for name, api in RESOURCE_APIS.items()
        }

        for future in concurrent.futures.as_completed(futures):
            name = futures[future]
            try:
                resource_name, count = future.result()
                if count != 'error' and count > 0:
                    accessible_resources.append((resource_name, count))
                    with open(summary_path, 'a') as summary:
                        summary.write(f"[+] List privilege on {resource_name}: {count} item(s)\n")
                elif count == 0:
                    accessible_resources.append((resource_name, count))
            except Exception as e:
                print(f"❌ Exception on '{name}': {e}")
            progress.update(1)

    progress.close()
    print("\n✅ Accesible resources:\n")
    for res in sorted(accessible_resources):
        if (res[1] == 0):
            print(f"⚠️ List privilege detected on '{res[0]}' but no resources found.")
        else:
            print(f"✅ List privilege detected on '{res[0]}' —— {res[1]} item(s) saved.")

    print(f"\n📁 Report saved to: {output_dir}/\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Audit LIST permissions across Google Cloud resources.")
    parser.add_argument('--project', required=True, help='GCP project ID')
    parser.add_argument('--token', required=True, help='Access token with required scopes')
    parser.add_argument('--output', default='output', help='Output directory for resource data')
    args = parser.parse_args()

    main(args.project, args.token, args.output)
