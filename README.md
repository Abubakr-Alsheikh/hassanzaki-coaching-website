### Setting Up the Environment Variables

To securely manage the Django secret key, follow these steps to create a `.env` file:

1. Create a file named `.env` in the root directory of your project.
2. Inside the `.env` file, add the following line:
    ```plaintext
    SECRET_KEY=your_secret_key_here
    ```
   Replace `your_secret_key_here` with your actual secret key.

3. Ensure your Django settings file fetches the secret key from the environment variable. Your `settings/base.py` should have the following line:
    ```python
    SECRET_KEY = os.getenv('SECRET_KEY')
    ```

By using environment variables, you can enhance the security of your application by keeping sensitive information out of your source code.