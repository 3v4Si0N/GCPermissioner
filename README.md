# GCPermissioner

**Audit your Google Cloud Platform (GCP) project for LIST permissions — fast, efficient, and with visibility.**

GCPermissioner is a Python 3 tool that scans across multiple GCP services using your access token, identifies which resources you can list, and saves a sample of accessible data for auditing or compliance review.

---

## ✨ Features

- 🔍 Detects active LIST permissions across dozens of GCP APIs  
- 📥 Fetches and stores resource samples in structured JSON files  
- 🧾 Generates a clean summary report  
- ⚡ Multi-threaded for performance  
- 📊 Progress bar and human-readable terminal feedback  
- 💼 Easy to integrate with security audits or CI/CD pipelines  

---

## 📂 Sample Output

```
✅ Access granted for 'compute_instances' — 4 item(s) saved.
✅ Access granted for 'cloud_storage_buckets' — 2 item(s) saved.
⚠️ LIST permission on 'firestore_databases' granted but no resources found.
```

Folder structure:

```
output/
├── summary.txt
├── compute_instances.json
├── cloud_storage_buckets.json
└── ...
```

---

## ⚙️ Requirements

- Python 3.7+
- `requests`
- `tqdm`

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🚀 Usage

```bash
python3 gcp_permissioner.py --project YOUR_PROJECT_ID --token ACCESS_TOKEN [--output ./output_folder]
```

**Arguments**:
- `--project`: Your GCP Project ID  
- `--token`: Access token with sufficient scopes (e.g., `https://www.googleapis.com/auth/cloud-platform.read-only`)  
- `--output`: *(Optional)* Directory to store output files (default: `./output`)  

---

## 💡 Example

```bash
python3 gcp_permissioner.py --project my-gcp-project --token ya29.a0... --output gcp_audit
```

```bash
python3 gcp_permissioner.py --project my-gcp-project --token $(gcloud auth print-access-token) --output gcp_audit
```

---

## 📌 Supported Resources

The tool currently supports LIST queries across services such as:

- Compute Engine  
- Cloud Storage  
- Cloud SQL  
- IAM Roles & Service Accounts  
- Cloud Functions  
- Firestore  
- Pub/Sub  
- and many more...

Easily extend support by editing the `RESOURCE_APIS` dictionary in the script.

**Still in development, need to add more resources**

---

## ⚠️ Disclaimer

This tool does not modify any resources. It is intended for **read-only auditing** purposes using public GCP APIs. Use only on GCP projects where you have explicit permission.

---

## 📄 License

GNU GPLv3

---

## 👨‍💻 Author

Built with passion by **3v4Si0N** — where offensive security meets cloud visibility.

---
