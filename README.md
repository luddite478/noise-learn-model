## Noise Gen Model

### Dependencies
- Docker
- MLflow server
- S3 server (required for MLflow)
- Prefect server (used for orchestrating scripts within flows/)
- Docker registry (To handle remote Prefect flow runs)

### Initialization
To initialize the project, run:
```
make init
```

### Setting Up Environment Variables
Fill values in the `.local.env` file

### Building Docker Image
```
make docker-build
```

### Pushing Docker Image
```
make docker-push
```

### Data Download Options
You have two options for setting up input data:
1. Run the command:
   ```
   make download
   ```
2. Alternatively, manually place audio files in the directory:
   ```
   data/input_files
   ```

### Data Preprocessing
```
make preprocess
```

### Model Training
```
make train
```

### Data Generation
```
make generate
```

### Prefect Deployment
```
make prefect-deploy
```

### Run Prefect Deployment on the infrastructure
```
make run-training-pipeline-infra
```

