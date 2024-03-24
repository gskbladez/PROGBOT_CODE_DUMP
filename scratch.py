import requests
import json

notion_collection_id = "97e4a870-4673-4fc7-a2c7-3fb876e4d837"
notion_collection_view_id = "085a4095-0668-4722-a8ec-91ae6f56640c"
notion_collection_space_id = "678b1442-260b-497a-9bf3-0d6ab3938e0d"
notion_query_link = "https://www.notion.so/api/v3/queryCollection"

query="character sheet"



data = {
    # TODO: add version?
    "collection": {
        "id": notion_collection_id, "spaceId": notion_collection_space_id
    },
    "collectionView": {
        "id": notion_collection_view_id, "spaceId": notion_collection_space_id
    },
    "loader": {
        "type": "reducer",
        "reducers": {
            "collection_group_results": {
                "type": "results",
                "limit": 50,
            },
            "table:uncategorized:title:count": {
                "type": "aggregation",
                "aggregation":{
                        "property":"title",
                        "aggregator":"count",
                },
            },
        },
        "filter": { 
                "property": "Name:", 
                "formula": {
                    "rich_text": "character sheet",
                }    
        },
        "sort":
            [
                {"property":"g=]<","direction":"ascending"},
                {"property":"title","direction":"ascending"},
                {"property":"UjPS","direction":"descending"}
            ],
            "userTimeZone": "America/Chicago",
    }

}

r = requests.post(notion_query_link, json=data)

if r.status_code != 200:
    print(r.status_code, r.reason)
    print("Response:", r.content)

# just leaving this here for the next time i need to work on this again..
parse = json.loads(r.content)
print(json.dumps(parse, indent=4, sort_keys=True))
