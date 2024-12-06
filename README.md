</head>
<body>
    <div class="container">
        <h1>📖 Manga Server: Your Personalized Manga Platform</h1>
        <p>A Django-based server project for managing a manga site, similar to MangaLib, with comprehensive features for users, manga, and comments.</p>

  <h2>✨ Features</h2>
        <ul>
            <li><strong>User Authentication</strong>: Full-featured authentication using JWT tokens for secure access.</li>
            <li><strong>CRUD Operations</strong>: Manage users, manga, and comments with endpoints for Create, Read, Update, and Delete operations.</li>
            <li><strong>Manga Reader Integration</strong>: Upload and read manga via a seamless API for the reader. Includes moderation features.</li>
            <li><strong>Media Management</strong>: Organized media storage with dedicated directories for:
                <ul>
                    <li>Users: Profile pictures and media.</li>
                    <li>Persons: Contributor or character images.</li>
                    <li>Manga: Covers, pages, and volumes.</li>
                </ul>
            </li>
        </ul>

  <h2>🛠️ Technology Stack</h2>
        <ul>
            <li><strong>Backend Framework</strong>: Django, Django Rest Framework (DRF)</li>
            <li><strong>Database</strong>: PostgreSQL</li>
        </ul>

<h2>🚀 Installation</h2>
        <ol>
            <li><strong>Clone the Repository</strong>:
                <pre><code>git clone https://github.com/FluffyTerror/djangoserver</code></pre>
            </li>
            <li><strong>Set Up Virtual Environment</strong>:
                <pre><code>python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate</code></pre>
            </li>
            <li><strong>Install Dependencies</strong>:
                <pre><code>pip install -r requirements.txt</code></pre>
            </li>
            <li><strong>Configure Database</strong>: Update the <code>DATABASES</code> settings in <code>settings.py</code> with your PostgreSQL credentials.</li>
            <li><strong>Apply Migrations</strong>:
                <pre><code>python manage.py migrate</code></pre>
            </li>
            <li><strong>Run the Server</strong>:
                <pre><code>python manage.py runserver</code></pre>
            </li>
            <li><strong>Access the Application</strong>: Open your browser and navigate to <a href="http://127.0.0.1:8000" target="_blank">http://127.0.0.1:8000</a>.</li>
        </ol>

<h2>🤝 Contributions</h2>
<p>Feel free to contribute! Fork the repository, make changes, and submit a pull request.</p>

</div>
</body>
</html>
