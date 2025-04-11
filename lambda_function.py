import boto3
import os
import json
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
s3 = boto3.client('s3')

OFFICERS_TABLE = os.environ.get('DYNAMODB_TABLE', 'Officers')
BLOGS_TABLE = os.environ.get('BLOGS_TABLE', 'Blogs')
OFFICERS_BUCKET = os.environ.get('S3_BUCKET', 'officers-profile-photos')
BLOGS_BUCKET = os.environ.get('BLOGS_BUCKET', 'blogs-markdown-files')

def lambda_handler(event, context):
    try:
        method = event.get('httpMethod')
        path = event.get('resource')
        query = event.get('queryStringParameters') or {}
        body = json.loads(event.get('body') or "{}")

        print(f"Method: {method}, Path: {path}, Query: {query}")

        route_map = {
            ("GET", "/officers"): lambda: get_officers(query),
            ("GET", "/blogs"): lambda: get_blogs(query),
            ("POST", "/blogs"): lambda: post_blog(body)
        }

        handler = route_map.get((method, path))
        if handler:
            return handler()
        else:
            return {
                'statusCode': 405,
                'body': json.dumps({'message': f'Method {method} not allowed on {path}'})
            }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error', 'details': str(e)})
        }

def generate_presigned_url(bucket_name, object_key, expiration=60):
    try:
        return s3.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': object_key}, ExpiresIn=expiration)
    except ClientError as e:
        print(e)
        return None

def get_officers(query):
    table = dynamodb.Table(OFFICERS_TABLE)
    if 'OfficerID' in query:
        return fetch_single_officer(table, query['OfficerID'])

    response = table.scan()
    officers = response.get('Items', [])
    for officer in officers:
        officer_id = officer['OfficerID']
        officer['PhotoS3URL'] = generate_presigned_url(OFFICERS_BUCKET, f"{officer_id}.jpg")

    return {'statusCode': 200, 'body': json.dumps(officers)}

def fetch_single_officer(table, officer_id):
    response = table.get_item(Key={'OfficerID': officer_id})
    if 'Item' not in response:
        return {'statusCode': 404, 'body': json.dumps({'message': 'Officer not found'})}

    officer = response['Item']
    officer['PhotoS3URL'] = generate_presigned_url(OFFICERS_BUCKET, f"{officer_id}.jpg")
    return {'statusCode': 200, 'body': json.dumps(officer)}

def get_blogs(query):
    table = dynamodb.Table(BLOGS_TABLE)

    # Get a single blog
    if 'BlogID' in query:
        blog_id = query['BlogID']
        response = table.get_item(Key={'BlogID': blog_id})
        if 'Item' not in response:
            return {'statusCode': 404, 'body': json.dumps({'message': 'Blog not found'})}
        
        blog = response['Item']
        blog_key = f"{blog_id}.md"
        blog_url = generate_presigned_url(BLOGS_BUCKET, blog_key)
        blog['MarkdownS3URL'] = blog_url

        return {'statusCode': 200, 'body': json.dumps(blog)}

    # Get all blogs
    response = table.scan()
    blogs = response.get('Items', [])
    for blog in blogs:
        blog_id = blog.get('BlogID')
        if blog_id:
            blog_key = f"{blog_id}.md"
            blog_url = generate_presigned_url(BLOGS_BUCKET, blog_key)
            blog['MarkdownS3URL'] = blog_url

    return {'statusCode': 200, 'body': json.dumps(blogs)}


def fetch_single_blog(table, blog_id):
    response = table.get_item(Key={'BlogID': blog_id})
    if 'Item' not in response:
        return {'statusCode': 404, 'body': json.dumps({'message': 'Blog not found'})}

    blog = response['Item']
    blog_key = f"{blog_id}.md"
    try:
        content_obj = s3.get_object(Bucket=BLOGS_BUCKET, Key=blog_key)
        blog['Content'] = content_obj['Body'].read().decode('utf-8')
    except Exception as e:
        blog['Content'] = f"Error retrieving blog content: {str(e)}"

    return {'statusCode': 200, 'body': json.dumps(blog)}

def post_blog(body):
    blog_id = body.get('BlogID')
    author = body.get('Author')
    title = body.get('Title')
    content = body.get('Content')

    if not all([blog_id, author, title, content]):
        return {'statusCode': 400, 'body': json.dumps({'message': 'Missing required fields'})}

    blog_key = f"{blog_id}.md"
    try:
        s3.put_object(Bucket=BLOGS_BUCKET, Key=blog_key, Body=content.encode('utf-8'))
        table = dynamodb.Table(BLOGS_TABLE)
        table.put_item(Item={
            'BlogID': blog_id,
            'Author': author,
            'Title': title,
            'S3Key': blog_key
        })
        return {'statusCode': 200, 'body': json.dumps({'message': 'Blog uploaded successfully'})}
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'message': 'Failed to upload blog', 'error': str(e)})}
