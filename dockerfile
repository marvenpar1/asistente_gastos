FROM public.ecr.aws/lambda/python:3.13

# Instalamos dependencias
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt

# Copy function code
COPY src/ ${LAMBDA_TASK_ROOT}/src/

# Asegurar que el handler esté en el PYTHONPATH
ENV PYTHONPATH="${LAMBDA_TASK_ROOT}/src"

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD ["src.app.main.lambda_handler"]