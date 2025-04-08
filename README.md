# lambda-dynamodb-s3

This project is a serverless application using AWS SAM (Serverless Application Model), AWS Lambda, DynamoDB, and S3. It exposes a REST API to fetch officer details stored in a DynamoDB table and their profile photos stored in an S3 bucket.

**Project Structure**

    lambda-dynamodb-s3/
    |-- lambda_function.py         # Lambda function code
    |-- template.yaml              # AWS SAM template for infrastructure
    |-- README.md                  # Project documentation

**AWS Resources**

    DynamoDB Table: Officers and Blogs
    
    S3 Bucket: officers-profile-photos and blogs-markdown-files
    
    Lambda Function: FetchOfficerDetailsFunction
    

**Prerequisites**

    AWS CLI configured
    
    AWS SAM CLI installed
    
    Python 3.8 or later

**Setup**

  1. Clone the repository:

    git clone https://github.com/curtxander/lambda-dynamodb-s3.git
    cd lambda-dynamodb-s3

  2. Build the project:
  
    sam build
  
  3. Deploy the project:
  
    sam deploy --guided

**API Endpoints**

**1. Get Officer by ID**
  
**Request:**
    
    curl "http://127.0.0.1:3000/officers?OfficerID=OFC12345"
  
**Response:**
  
    {
      "OfficerID": "OFC12345",
      "Name": "Curt Xander Bergano",
      "Position": "Backend Developer",
      "Description": "He is one of the backend developers of this website.",
      "LinkedInURL": "https://www.linkedin.com/in/curt-xander-bergano-5a7a08205/",
      "PhotoS3URL": "https://s3.amazonaws.com/officers-profile-photos/OFC12345.jpg"
    }

**2. Get All Officers**
  
**Request:**
    
    curl "http://127.0.0.1:3000/officers"
    
**Response:**

    [
      {
        "OfficerID": "OFC12345",
        "Name": "John Doe",
        "Position": "Department Head",
        "Description": "Experienced leader in academic affairs.",
        "LinkedInURL": "https://linkedin.com/in/johndoe",
        "PhotoS3URL": "https://s3.amazonaws.com/officers-profile-photos/OFC12345.jpg"
      },
      {
        "OfficerID": "OFC67890",
        "Name": "Jane Smith",
        "Position": "Project Manager",
        "Description": "Expert in project delivery.",
        "LinkedInURL": "https://linkedin.com/in/janesmith",
        "PhotoS3URL": "https://s3.amazonaws.com/officers-profile-photos/OFC67890.jpg"
      }
    ]

**3. Get Blogs by ID**
  
**Request:**
    
    curl "http://127.0.0.1:3000/blogs?BlogID=blog001"
    
**Response:**

     {
    "Title": "My First Blog",
    "Author": "Curt Bergano",
    "BlogID": "blog001",
    "MarkdownS3URL": "https://blogs-markdown-files.s3.amazonaws.com/blog001.md?AWSAccessKeyId=AKIATTSKFMFHENZMGKNG&Signature=5xmUFgrZ6uJyoIP842jyH3icuvg%3D&Expires=1744075766"
  }


**DynamoDB Table Structure**

    Attribute       Type
  
      OfficerID        String
      
      Name             String
      
      Position         String
      
      Description      String
      
      LinkedInURL      String
      
      PhotoS3URL       String

    Attribute       Type
  
      BlogID          String
      
      Author          String
      
      Title           String

      MarkdownS3URl   String

**S3 Bucket Structure**

  officers-profile-photos/
  
    |-- OFC12345.jpg
    
    |-- OFC67890.jpg

  blogs-markdown-files/
  
    |-- blog001.md
    
    |-- blog002.md
    
**Local Development**

  1. Start the API locally:
  
    sam local start-api

  2. Test the API:

    curl "http://127.0.0.1:3000/officers?OfficerID=OFC12345"

**Troubleshooting**

  Internal Server Error: Ensure the IAM role attached to the Lambda function has permissions for DynamoDB and S3.

  Empty Response: Ensure the OfficerID exists in the DynamoDB table.

  Photo Not Found: Ensure the photo exists in the S3 bucket with the correct name.


