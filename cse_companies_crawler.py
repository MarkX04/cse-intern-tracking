import requests
import time
import json
import os

# Sử dụng session để tái sử dụng kết nối
session = requests.Session()

def crawl_basic_companies():
    url = "https://internship.cse.hcmut.edu.vn/home/company/all?t=1744093866515&condition="
    try:
        response = session.get(url, timeout=10)
    except Exception as e:
        print(f"Error connection: {e}")
        return {}

    companies = {}
    
    if response.status_code == 200:
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            print(f"Error decode: {e}")
            return {}
        
        if isinstance(data, dict) and "items" in data:
            companies_list = data["items"]
        elif isinstance(data, list):
            companies_list = data
        else:
            companies_list = []
        
        for company in companies_list:
            if not isinstance(company, dict):
                continue
            comp_id = company.get("_id")
            if comp_id:
                companies[comp_id] = {
                    "id": comp_id,
                    "shortname": company.get("shortname", ""),
                    "fullname": company.get("fullname", ""),
                    "isSponsor": company.get("isSponsor", False),
                    "image": company.get("image", ""),
                    "level": company.get("level"),
                    "width": company.get("width"),
                    "height": company.get("height")
                }
        print("Finished crawling all the companies:", time.ctime())
    else:
        print("Error:", response.status_code)
    
    return companies

def crawl_company_detail(company_id):
    timestamp = int(time.time() * 1000)
    detail_url = f"https://internship.cse.hcmut.edu.vn/home/company/id/{company_id}?t={timestamp}"
    try:
        detail_resp = session.get(detail_url, timeout=10)
    except Exception as e:
        print(f"Error connection for {company_id}: {e}")
        return None

    if detail_resp.status_code == 200:
        try:
            detail_data = detail_resp.json()
        except json.JSONDecodeError as e:
            print(f"Decode error for {company_id}: {e}")
            return None

        if detail_data.get("error") is None:
            item = detail_data.get("item", {})
            detail = {
                "address": item.get("address", ""),
                "studentRegister": item.get("studentRegister", 0),
                "studentAccepted": item.get("studentAccepted", 0),
                "maxRegister": item.get("maxRegister", 0),
                "maxAcceptedStudent": item.get("maxAcceptedStudent", 0),
                "adminMaxRegister": item.get("adminMaxRegister", 0),
                "acceptedIntern": item.get("acceptedIntern", False),
                "subscribeAcceptedEmail": item.get("subscribeAcceptedEmail", False),
                "active": item.get("active", True),
                "description": item.get("description", ""),
                "internshipFiles": item.get("internshipFiles", []),
                "work": item.get("work", "")
            }
            return detail
        else:
            print(f"Error responses for {company_id}: {detail_data.get('error')}")
    else:
        print(f"Error {company_id}: {detail_resp.status_code}")
    
    return None

def update_company_history(company_id, metrics, folder="data_histories"):
    file_path = os.path.join(folder, f"{company_id}.json")
    history = []
    
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                history = json.load(f)
        except json.JSONDecodeError:
            history = []
    
    metrics["timestamp"] = int(time.time())
    history.append(metrics)
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        print(f"Updated data history for {company_id}")
    except Exception as e:
        print(f"Error {company_id}: {e}")

def crawl_all_companies():
    companies = crawl_basic_companies()
    for comp_id in companies.keys():
        detail = crawl_company_detail(comp_id)
        if detail:
            companies[comp_id].update(detail)
            metrics = {
                "studentRegister": detail.get("studentRegister", 0),
                "studentAccepted": detail.get("studentAccepted", 0),
                "maxRegister": detail.get("maxRegister", 0),
                "maxAcceptedStudent": detail.get("maxAcceptedStudent", 0)
            }
            update_company_history(comp_id, metrics)
        time.sleep(1)
    return companies

def main():
    companies_data = crawl_all_companies()
    with open("companies.json", "w", encoding="utf-8") as f:
        json.dump(companies_data, f, ensure_ascii=False, indent=2)
        
if __name__ == "__main__":
    main()
