from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import os
import random

# --- Configuration ---
app = Flask(__name__)
app.secret_key = 'supersecretkey_for_job_board_app'  # Replace with a strong, random key in production

# Ensure data directory exists
data_dir = 'data'
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Database setup
DATABASE_URL = 'sqlite:///./data/jobs.db'
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()
Session = sessionmaker(bind=engine)
db_session = Session()

# --- Model ---
class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, nullable=False)
    job_type = Column(String, nullable=False)  # Full-time, Part-time, Remote, Contract
    description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=False)
    salary_range = Column(String)
    how_to_apply = Column(Text, nullable=False)
    posted_date = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Job {self.title} at {self.company}>"

# --- Database Seeding ---
def seed_database():
    Base.metadata.create_all(engine)
    if db_session.query(Job).count() == 0:
        print("Seeding database with initial job postings...")
        job_postings = [
            Job(
                title="Senior Python Developer",
                company="Tech Innovators Inc.",
                location="San Francisco, CA",
                job_type="Full-time",
                description="Seeking a talented Senior Python Developer to build scalable backend services.",
                requirements="5+ years of Python experience, strong knowledge of Flask/Django, SQL, AWS.",
                salary_range="$120,000 - $160,000",
                how_to_apply="Apply directly on our company website: careers.techinnovators.com/python-dev"
            ),
            Job(
                title="Marketing Manager",
                company="Creative Solutions Co.",
                location="New York, NY (Remote-friendly)",
                job_type="Full-time",
                description="Lead our marketing efforts, develop strategies, and manage campaigns.",
                requirements="3+ years in marketing, excellent communication, experience with digital marketing tools.",
                salary_range="$70,000 - $90,000",
                how_to_apply="Send resume and cover letter to jobs@creativesolutions.com"
            ),
            Job(
                title="Remote Frontend Engineer (React)",
                company="Global Web Works",
                location="Remote",
                job_type="Remote",
                description="Develop user-facing features using React.js and modern web technologies.",
                requirements="2+ years of React experience, JavaScript, HTML, CSS, strong portfolio.",
                salary_range="$90,000 - $110,000",
                how_to_apply="Apply via LinkedIn: linkedin.com/jobs/global-web-works-frontend"
            ),
            Job(
                title="Part-time Graphic Designer",
                company="Design Studio X",
                location="Austin, TX",
                job_type="Part-time",
                description="Create stunning visual content for web and print.",
                requirements="Proficiency in Adobe Creative Suite, portfolio required, 1-2 years experience.",
                salary_range="$25 - $35/hour",
                how_to_apply="Email portfolio to hr@designstudiox.com"
            ),
            Job(
                title="Data Scientist (Contract)",
                company="Analytics Gurus",
                location="Boston, MA",
                job_type="Contract",
                description="Analyze complex datasets, build predictive models, and provide insights.",
                requirements="PhD/Masters in a quantitative field, Python/R, machine learning, SQL.",
                salary_range="$60 - $80/hour",
                how_to_apply="Contact recruiter at apply@analyticsgurus.com with your CV."
            ),
            Job(
                title="DevOps Engineer",
                company="Cloud Solutions Ltd.",
                location="Seattle, WA",
                job_type="Full-time",
                description="Build and maintain CI/CD pipelines, manage cloud infrastructure (AWS/Azure).",
                requirements="3+ years of DevOps, Docker, Kubernetes, strong scripting skills (Bash/Python).",
                salary_range="$100,000 - $130,000",
                how_to_apply="Apply through our portal: careers.cloudsolutions.com/devops"
            ),
            Job(
                title="Product Manager",
                company="Innovation Hub",
                location="San Francisco, CA",
                job_type="Full-time",
                description="Define product strategy, roadmaps, and requirements for our next-gen products.",
                requirements="5+ years in product management, strong leadership, excellent communication.",
                salary_range="$110,000 - $150,000",
                how_to_apply="Submit your application on our website: innovationhub.com/product-manager"
            ),
            Job(
                title="Customer Support Specialist",
                company="UserFirst Tech",
                location="Remote",
                job_type="Remote",
                description="Provide exceptional support to our customers, resolving inquiries and issues.",
                requirements="1+ year in customer service, excellent problem-solving, strong communication.",
                salary_range="$40,000 - $55,000",
                how_to_apply="Apply here: userfirsttech.com/support-jobs"
            ),
            Job(
                title="Backend Java Developer",
                company="Enterprise Software Inc.",
                location="Chicago, IL",
                job_type="Full-time",
                description="Design and implement robust backend systems using Java and Spring Boot.",
                requirements="4+ years of Java development, Spring Boot, RESTful APIs, database experience.",
                salary_range="$100,000 - $140,000",
                how_to_apply="Send your CV to careers@enterprisesoft.com"
            ),
            Job(
                title="UI/UX Designer",
                company="Aesthetic Apps",
                location="Los Angeles, CA",
                job_type="Full-time",
                description="Create intuitive and visually appealing user interfaces and experiences.",
                requirements="3+ years of UI/UX design, Figma/Sketch, strong portfolio, user-centered design.",
                salary_range="$80,000 - $110,000",
                how_to_apply="Apply on our career page: aestheticapps.com/design-roles"
            ),
            Job(
                title="Technical Writer",
                company="Documentation Masters",
                location="Remote",
                job_type="Contract",
                description="Produce high-quality technical documentation for software products.",
                requirements="2+ years of technical writing, excellent written communication, attention to detail.",
                salary_range="$45 - $65/hour",
                how_to_apply="Email samples and CV to writer@docmasters.com"
            ),
            Job(
                title="HR Generalist",
                company="People Solutions Group",
                location="Dallas, TX",
                job_type="Full-time",
                description="Manage various HR functions, including recruitment, onboarding, and employee relations.",
                requirements="3+ years of HR experience, strong knowledge of labor laws, excellent interpersonal skills.",
                salary_range="$60,000 - $80,000",
                how_to_apply="Apply through our website: peoplesolutions.com/hr-careers"
            )
        ]
        db_session.add_all(job_postings)
        db_session.commit()
        print("Database seeding complete.")
    else:
        print("Database already contains job postings. Skipping seeding.")

# Run seeding on startup
with app.app_context():
    seed_database()

# --- Authentication ---
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

def is_authenticated():
    return session.get('logged_in')

def login_required(f):
    import functools
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---

@app.route('/')
def index():
    query = request.args.get('q', '')
    job_type_filter = request.args.get('type', '')

    jobs = db_session.query(Job).order_by(Job.posted_date.desc())

    if query:
        search_pattern = f"%{query}%"
        jobs = jobs.filter(
            (Job.title.ilike(search_pattern)) |
            (Job.company.ilike(search_pattern)) |
            (Job.description.ilike(search_pattern))
        )

    if job_type_filter:
        jobs = jobs.filter(Job.job_type == job_type_filter)

    job_types = sorted(list(set([job.job_type for job in db_session.query(Job.job_type).distinct().all()])))

    return render_template('index.html', jobs=jobs.all(), query=query, job_type_filter=job_type_filter, job_types=job_types)

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    job = db_session.query(Job).get_or_404(job_id)
    return render_template('detail.html', job=job)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin_post'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/admin/post', methods=['GET', 'POST'])
@login_required
def admin_post():
    if request.method == 'POST':
        new_job = Job(
            title=request.form['title'],
            company=request.form['company'],
            location=request.form['location'],
            job_type=request.form['job_type'],
            salary_range=request.form['salary_range'],
            description=request.form['description'],
            requirements=request.form['requirements'],
            how_to_apply=request.form['how_to_apply']
        )
        db_session.add(new_job)
        db_session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('post.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/health')
def health_check():
    return jsonify({"status": "ok"})

# --- Run Application ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
