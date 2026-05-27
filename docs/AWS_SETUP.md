# AWS Setup For EC2 + AWS Glue Analytics

This project now supports two analytics modes:

- `local`: run PySpark on the app server
- `aws_glue`: run PySpark as an AWS Glue job

For your current goal, use `aws_glue`.

## Architecture

- `EC2` hosts the FastAPI backend, React build, SQLite database, and local uploads
- `S3` stores analytics input snapshots and analytics result JSON
- `AWS Glue` runs the PySpark job from [aws/glue/smart_notes_analytics_job.py](/e:/Projects/CC-2/aws/glue/smart_notes_analytics_job.py)

## 1. Create An S3 Bucket

Create one bucket, for example:

```text
smart-notes-analytics-<unique-suffix>
```

Use the same Region as your EC2 instance and Glue job.

Keep Block Public Access enabled.

## 2. Upload The Glue Script

Upload this file from the repo to S3:

```text
aws/glue/smart_notes_analytics_job.py
```

Suggested key:

```text
glue/scripts/smart_notes_analytics_job.py
```

So the final script path looks like:

```text
s3://<YOUR_BUCKET>/glue/scripts/smart_notes_analytics_job.py
```

## 3. Create The AWS Glue Job

Open `AWS Glue` in the console and create a job with:

- Job name: `smart-notes-analytics`
- IAM role: use the default Glue service role if Learner Lab provides it, or create the allowed Glue role if your lab permits it
- Job type: `Spark`
- Language: `Python`
- Glue version: `4.0` or later
- Worker type: the smallest available worker type in your lab
- Number of workers: `2`
- Script path: the S3 script path from step 2

### Job parameters

Add:

```text
--TempDir=s3://<YOUR_BUCKET>/glue/temp/
```

AWS Glue documents that Spark job arguments such as `--TempDir` and script location are provided through job arguments and S3 paths. See:

- https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-etl-glue-arguments.html
- https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-python.html

## 4. Give The App Access To S3 And Glue

Your EC2 app must be able to:

- `s3:PutObject`
- `s3:GetObject`
- `glue:StartJobRun`
- `glue:GetJobRun`

In Learner Lab, the cleanest option is usually the lab-provided temporary credentials in `.env`.

If instance roles are available in your lab, that is better than hardcoding temporary credentials.

## 5. Configure Backend Environment Variables

On EC2, edit:

```bash
nano ~/smart-notes/backend/.env
```

Set at least:

```env
SECRET_KEY="replace-with-a-long-random-secret"
DEBUG=False
ANALYTICS_ENGINE="aws_glue"
AWS_REGION="us-east-1"
AWS_BUCKET_NAME="<YOUR_BUCKET>"
AWS_ANALYTICS_BUCKET_NAME="<YOUR_BUCKET>"
AWS_GLUE_JOB_NAME="smart-notes-analytics"
AWS_ANALYTICS_INPUT_PREFIX="analytics/input"
AWS_ANALYTICS_OUTPUT_PREFIX="analytics/output"
```

If your Learner Lab requires temporary credentials, also set:

```env
AWS_ACCESS_KEY_ID="..."
AWS_SECRET_ACCESS_KEY="..."
AWS_SESSION_TOKEN="..."
```

## 6. Restart The API

```bash
pm2 restart smart-notes-api
```

## 7. How It Works At Runtime

When a user opens the analytics page:

1. The backend reads that user's notes from SQLite.
2. It writes a small JSON snapshot to S3.
3. It starts the AWS Glue PySpark job with `StartJobRun`.
4. The Glue job computes analytics and writes a JSON result back to S3.
5. The frontend polls until the result is ready.

AWS Glue `StartJobRun` is documented here:

- https://docs.aws.amazon.com/glue/latest/webapi/API_StartJobRun.html
- https://docs.aws.amazon.com/boto3/latest/reference/services/glue/client/start_job_run.html

## 8. Important Learner Lab Advice

- Glue startup can take time, so the first analytics run may sit in `running` state for a bit.
- Stop or clean up EC2 and Glue resources when you are done.
- Keep everything in one Region to avoid confusion and extra cost.

## 9. If Glue Is Not Available In Your Lab

If your specific Learner Lab account blocks Glue job creation, the fallback is:

1. Deploy on EC2 exactly as prepared here.
2. Set `ANALYTICS_ENGINE="local"`.
3. Run PySpark on the EC2 host itself.

That is still AWS-hosted, but not AWS-managed Spark.
