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
        path = event['resource']
        query = event.get('queryStringParameters') or {}
        print(f"Path: {path}, Query: {query}")  # Debugging line to see incoming request

        if path == "/officers":
            return get_officers(query)
        elif path == "/blogs":
            return get_blogs(query)
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Path not found'})
            }

    except Exception as e:
        print(f"Error: {str(e)}")  # Log the error message
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error', 'details': str(e)})
        }

def generate_presigned_url(bucket_name, object_key, expiration=60):
    """Generate a pre-signed URL to share an S3 object."""
    try:
        url = s3.generate_presigned_url('get_object',
                                       Params={'Bucket': bucket_name, 'Key': object_key},
                                       ExpiresIn=expiration)
        return url
    except ClientError as e:
        print(e)
        return None

def get_officers(query):
    table = dynamodb.Table(OFFICERS_TABLE)
    output = ""

    if 'OfficerID' in query:
        officer_id = query['OfficerID']
        response = table.get_item(Key={'OfficerID': officer_id})
        if 'Item' not in response:
            return {'statusCode': 404, 'body': json.dumps({'message': 'Officer not found'})}
        officer = response['Item']
        photo_key = f"{officer_id}.jpg"
        
        # Generate pre-signed URL for officer photo
        photo_url = generate_presigned_url(OFFICERS_BUCKET, photo_key)
        officer['PhotoS3URL'] = photo_url
        
        output = json.dumps(officer)
        for chunk in [output[i:i+1000] for i in range(0, len(output), 1000)]:
            print(chunk) 
        return {'statusCode': 200, 'body': output}

    # Return all officers
    response = table.scan()
    officers = response.get('Items', [])
    for officer in officers:
        officer_id = officer['OfficerID']
        photo_key = f"{officer_id}.jpg"
        
        # Generate pre-signed URL for officer photo
        photo_url = generate_presigned_url(OFFICERS_BUCKET, photo_key)
        officer['PhotoS3URL'] = photo_url
        
    output = json.dumps(officers)
    for chunk in [output[i:i+1000] for i in range(0, len(output), 1000)]:
        print(chunk) 
    return {'statusCode': 200, 'body': output}

def get_blogs(query):
    table = dynamodb.Table(BLOGS_TABLE)
    output = ""

    if 'BlogID' in query:
        blog_id = query['BlogID']
        response = table.get_item(Key={'BlogID': blog_id})
        if 'Item' not in response:
            return {'statusCode': 404, 'body': json.dumps({'message': 'Blog not found'})}
        blog = response['Item']
        blog_key = f"{blog_id}.md"
        
        # Generate pre-signed URL for blog markdown file
        blog_url = generate_presigned_url(BLOGS_BUCKET, blog_key)
        blog['MarkdownS3URL'] = blog_url
        
        output = json.dumps(blog)
        for chunk in [output[i:i+1000] for i in range(0, len(output), 1000)]:
            print(chunk)
        return {'statusCode': 200, 'body': output}

    # Return all blogs (only Author and Title)
    response = table.scan()
    blogs = response.get('Items', [])
    for blog in blogs:
        blog_id = blog['BlogID']
        blog_key = f"{blog_id}.md"
        
        # Generate pre-signed URL for blog markdown file
        blog_url = generate_presigned_url(BLOGS_BUCKET, blog_key)
        blog['MarkdownS3URL'] = blog_url
        
    output = json.dumps(blogs)
    for chunk in [output[i:i+1000] for i in range(0, len(output), 1000)]:
        print(chunk)
    return {'statusCode': 200, 'body': output}

