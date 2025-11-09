from flask import Flask, render_template, abort
import markdown
import frontmatter
import os
from datetime import datetime
from dateutil import parser as date_parser

app = Flask(__name__)

# Helper function to get all posts
def get_posts():
    """
    Load all markdown files from posts/ directory,
    parse their frontmatter, and return a sorted list.
    """
    posts = []
    posts_dir = 'posts'
    
    # Check if posts directory exists
    if not os.path.exists(posts_dir):
        return posts
    
    # Loop through all markdown files
    for filename in os.listdir(posts_dir):
        if filename.endswith('.md'):
            filepath = os.path.join(posts_dir, filename)
            
            # Read the markdown file with frontmatter
            with open(filepath, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
                
                # Extract slug from filename (remove .md and date prefix if present)
                # Example: 2024-11-09-why-im-building-this.md -> why-im-building-this
                slug = filename.replace('.md', '')
                if len(slug) > 10 and slug[10] == '-':  # Has date prefix
                    slug = slug[11:]  # Remove YYYY-MM-DD- prefix
                
                # Create post object
                post_data = {
                    'title': post.get('title', 'Untitled'),
                    'date': post.get('date'),
                    'excerpt': post.get('excerpt', ''),
                    'content': post.content,
                    'slug': slug,
                    'filename': filename
                }
                
                posts.append(post_data)
    
    # Sort posts by date (newest first)
    posts.sort(key=lambda x: x['date'] if x['date'] else datetime.min, reverse=True)
    
    return posts

# Helper function to get a single post
def get_post(slug):
    """
    Load a specific post by its slug.
    """
    posts_dir = 'posts'
    
    # Try to find the markdown file matching this slug
    for filename in os.listdir(posts_dir):
        if filename.endswith('.md'):
            # Check if slug matches (with or without date prefix)
            file_slug = filename.replace('.md', '')
            if len(file_slug) > 10 and file_slug[10] == '-':
                file_slug = file_slug[11:]
            
            if file_slug == slug:
                filepath = os.path.join(posts_dir, filename)
                
                # Read and parse the post
                with open(filepath, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)
                    
                    # Convert markdown to HTML
                    html_content = markdown.markdown(
                        post.content,
                        extensions=['fenced_code', 'codehilite', 'tables']
                    )
                    
                    return {
                        'title': post.get('title', 'Untitled'),
                        'date': post.get('date'),
                        'content': html_content,
                        'slug': slug
                    }
    
    return None

# Routes
@app.route('/')
def index():
    """Homepage - list all blog posts"""
    posts = get_posts()
    return render_template('index.html', posts=posts)

@app.route('/post/<slug>')
def post(slug):
    """Individual post page"""
    post_data = get_post(slug)
    
    if post_data is None:
        abort(404)
    
    return render_template('post.html', post=post_data)

@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 page"""
    return render_template('404.html'), 404

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=5000)