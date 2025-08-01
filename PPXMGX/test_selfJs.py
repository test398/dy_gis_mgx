import requests
import mapbox_vector_tile
import gzip

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
    'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJc3N1YW5jZSI6IlkiLCJhcHBJZCI6IjhkYzU0OThiZDcxMDMzYTA5OTJlNGQ3NzhhMDZlN2UzIiwiY2xpZW50SXAiOiIyMjMuNjUuNTcuMTYzIiwiZXhwIjoxNzUxODg1NjAzLCJpYXQiOjE3NTE4ODIwMDMsImlzcyI6Ind3dy5hZWdpcy5jb20iLCJqdGkiOiJDRFRSS1JYQlJKIiwic2NvcGVzIjo3LCJzdWIiOiI2Yzc5MDUwYTI5ODAzMTE4OTlkY2U3NzQ5MzI4OGI5MiIsInN1YlR5cGUiOiJhcHBrZXkiLCJ0b2tlblRUTCI6MzYwMDAwMCwidXNlck5hbWUiOiJ3ancifQ.nyW3o4SOxeyMkwCHnrNSsbV0m5Ie4IBMso8Kew-guTc',
    'Referer': 'https://map.sgcc.com.cn/',
}

response = requests.get(
    'https://map.sgcc.com.cn:21610/v1/aegis.SGPoi-Web.nBnK,aegis.SGAnchor-Web.nBnK,aegis.SGPolygon-Web.rynK,aegis.SGLine-Web.nBnK/12/3397/1317.sg',
    headers=headers,
    stream=True,
)

print(response.content[:100])
tile = mapbox_vector_tile.decode(response.content)
print(tile)