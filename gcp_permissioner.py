import argparse
import requests
import concurrent.futures
import os
import json
from tqdm import tqdm

# Resources dictionary
RESOURCE_APIS = {
    'compute_instances': {
        'url': 'https://compute.googleapis.com/compute/v1/projects/{project}/aggregated/instances',
        'key': 'items'
    },
    'cloud_storage_buckets': {
        'url': 'https://storage.googleapis.com/storage/v1/b?project={project}',
        'key': 'items'
    },
    'cloud_functions': {
        'url': 'https://cloudfunctions.googleapis.com/v1/projects/{project}/locations/-/functions',
        'key': 'functions'
    },
    'iam_roles': {
        'url': 'https://iam.googleapis.com/v1/projects/{project}/roles',
        'key': 'roles'
    },
    'cloud_sql_instances': {
        'url': 'https://sqladmin.googleapis.com/sql/v1beta4/projects/{project}/instances',
        'key': 'items'
    },
    'pubsub_topics': {
        'url': 'https://pubsub.googleapis.com/v1/projects/{project}/topics',
        'key': 'topics'
    },
    'firestore_databases': {
        'url': 'https://firestore.googleapis.com/v1/projects/{project}/databases',
        'key': 'databases'
    },
    'bigquery_datasets': {
        'url': 'https://bigquery.googleapis.com/bigquery/v2/projects/{project}/datasets',
        'key': 'datasets'
    },
    'kubernetes_clusters': {
        'url': 'https://container.googleapis.com/v1/projects/{project}/locations/-/clusters',
        'key': 'clusters'
    },
    'app_engine_services': {
        'url': 'https://appengine.googleapis.com/v1/apps/{project}/services',
        'key': 'services'
    },
    'bigtable_instances': {
        'url': 'https://bigtableadmin.googleapis.com/v2/projects/{project}/instances',
        'key': 'instances'
    },
    'spanner_instances': {
        'url': 'https://spanner.googleapis.com/v1/projects/{project}/instances',
        'key': 'instances'
    },
    'dataflow_jobs': {
        'url': 'https://dataflow.googleapis.com/v1b3/projects/{project}/jobs',
        'key': 'jobs'
    },
    'dataproc_clusters': {
        'url': 'https://dataproc.googleapis.com/v1/projects/{project}/regions/-/clusters',
        'key': 'clusters'
    },
    'cloud_run_services': {
        'url': 'https://run.googleapis.com/v1/projects/{project}/locations/-/services',
        'key': 'items'
    },
    'filestore_instances': {
        'url': 'https://file.googleapis.com/v1/projects/{project}/locations/-/instances',
        'key': 'instances'
    },
    'memorystore_redis_instances': {
        'url': 'https://redis.googleapis.com/v1/projects/{project}/locations/-/instances',
        'key': 'instances'
    },
    'memorystore_memcached_instances': {
        'url': 'https://memcache.googleapis.com/v1/projects/{project}/locations/-/instances',
        'key': 'instances'
    },
    'service_accounts': {
        'url': 'https://iam.googleapis.com/v1/projects/{project}/serviceAccounts',
        'key': 'accounts'
    },
    'endpoints_services': {
        'url': 'https://servicemanagement.googleapis.com/v1/services?consumerId=project:{project}',
        'key': 'services'
    },
    'cloud_tasks_queues': {
        'url': 'https://cloudtasks.googleapis.com/v2/projects/{project}/locations/-/queues',
        'key': 'queues'
    },
    'cloud_scheduler_jobs': {
        'url': 'https://cloudscheduler.googleapis.com/v1/projects/{project}/locations/-/jobs',
        'key': 'jobs'
    },
    'secret_manager_secrets': {
        'url': 'https://secretmanager.googleapis.com/v1/projects/{project}/secrets',
        'key': 'secrets'
    },
    'iot_registries': {
        'url': 'https://cloudiot.googleapis.com/v1/projects/{project}/locations/-/registries',
        'key': 'deviceRegistries'
    },
    'notebooks_instances': {
        'url': 'https://notebooks.googleapis.com/v1/projects/{project}/locations/-/instances',
        'key': 'instances'
    },
    'composer_environments': {
        'url': 'https://composer.googleapis.com/v1/projects/{project}/locations/-/environments',
        'key': 'environments'
    },
    'artifact_registry_repositories': {
        'url': 'https://artifactregistry.googleapis.com/v1/projects/{project}/locations/-/repositories',
        'key': 'repositories'
    },
    'cloud_build_triggers': {
        'url': 'https://cloudbuild.googleapis.com/v1/projects/{project}/triggers',
        'key': 'triggers'
    },
    'recaptcha_keys': {
        'url': 'https://recaptchaenterprise.googleapis.com/v1/projects/{project}/keys',
        'key': 'keys'
    },
    'cloud_deploy_delivery_pipelines': {
        'url': 'https://clouddeploy.googleapis.com/v1/projects/{project}/locations/-/deliveryPipelines',
        'key': 'deliveryPipelines'
    },
    'game_services_realms': {
        'url': 'https://gameservices.googleapis.com/v1/projects/{project}/locations/-/realms',
        'key': 'realms'
    },
    'beyondcorp_applications': {
        'url': 'https://beyondcorp.googleapis.com/v1/projects/{project}/locations/-/applications',
        'key': 'applications'
    },
    'datastream_streams': {
        'url': 'https://datastream.googleapis.com/v1/projects/{project}/locations/-/streams',
        'key': 'streams'
    },
    'eventarc_triggers': {
        'url': 'https://eventarc.googleapis.com/v1/projects/{project}/locations/-/triggers',
        'key': 'triggers'
    },
    'vertex_ai_endpoints': {
        'url': 'https://us-central1-aiplatform.googleapis.com/v1/projects/{project}/locations/us-central1/endpoints',
        'key': 'endpoints'
    },
    'workflows': {
        'url': 'https://workflowexecutions.googleapis.com/v1/projects/{project}/locations/-/workflows',
        'key': 'workflows'
    },
    'bare_metal_solution_instances': {
        'url': 'https://baremetalsolution.googleapis.com/v2/projects/{project}/locations/-/instances',
        'key': 'instances'
    },
    'cloud_identity_groups': {
        # NOTA: Requiere customer_id. Este se puede obtener con otra API si se desea automatizar.
        'url': 'https://cloudidentity.googleapis.com/v1/groups?parent=customers/my_customer',
        'key': 'groups'
    },
    'cloud_dns_managed_zones': {
        'url': 'https://dns.googleapis.com/dns/v1/projects/{project}/managedZones',
        'key': 'managedZones'
    },
    'cloud_dns_policies': {
        'url': 'https://dns.googleapis.com/dns/v1/projects/{project}/policies',
        'key': 'policies'
    },
    'access_context_manager_policies': {
        'url': 'https://accesscontextmanager.googleapis.com/v1/accessPolicies',
        'key': 'accessPolicies'
    },
    'access_context_manager_perimeters': {
        'url': 'https://accesscontextmanager.googleapis.com/v1/accessPolicies/-/accessLevels',
        'key': 'accessLevels'
    },
    'vpc_access_connectors': {
        'url': 'https://vpcaccess.googleapis.com/v1/projects/{project}/locations/-/connectors',
        'key': 'connectors'
    },
    'netapp_volumes': {
        'url': 'https://netapp.googleapis.com/v1/projects/{project}/locations/-/volumes',
        'key': 'volumes'
    },
    'gke_hub_memberships': {
        'url': 'https://gkehub.googleapis.com/v1/projects/{project}/locations/global/memberships',
        'key': 'resources'
    },
    'dataplex_lakes': {
        'url': 'https://dataplex.googleapis.com/v1/projects/{project}/locations/-/lakes',
        'key': 'lakes'
    },
    'dataplex_zones': {
        'url': 'https://dataplex.googleapis.com/v1/projects/{project}/locations/-/lakes/-/zones',
        'key': 'zones'
    },
    'billing_accounts': {
        'url': 'https://cloudbilling.googleapis.com/v1/billingAccounts',
        'key': 'billingAccounts'
    },
    'monitoring_alert_policies': {
        'url': 'https://monitoring.googleapis.com/v3/projects/{project}/alertPolicies',
        'key': 'alertPolicies'
    },
    'monitoring_dashboards': {
        'url': 'https://monitoring.googleapis.com/v1/projects/{project}/dashboards',
        'key': 'dashboards'
    },
    'cloudresourcemanager_folders': {
        'url': 'https://cloudresourcemanager.googleapis.com/v2/folders',
        'key': 'folders'
    },
    'cloudresourcemanager_projects': {
        'url': 'https://cloudresourcemanager.googleapis.com/v1/projects',
        'key': 'projects'
    }
}

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
