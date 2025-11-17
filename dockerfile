FROM public.ecr.aws/lambda/python:3.13

# Instalamos dependencias
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código fuente
COPY src/ ${LAMBDA_TASK_ROOT}/src/

# Aseguramos que src está en el PYTHONPATH
ENV PYTHONPATH="${LAMBDA_TASK_ROOT}/src"

# OJO con el handler:
# Si tu función está en src/app/main.py y se llama lambda_handler,
# el módulo es "app.main", NO "src.app.main"
CMD ["app.main.lambda_handler"]
