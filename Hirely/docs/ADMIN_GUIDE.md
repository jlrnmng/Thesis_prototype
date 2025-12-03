# Hirely Admin Guide - Employers & Recruiters

**Version:** 1.0  
**Last Updated:** December 3, 2025

Welcome to Hirely's Admin Portal! This guide will help you effectively manage job postings, review candidates, and make the most of our AI-powered recruitment system.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Creating Your Admin Account](#creating-your-admin-account)
3. [Understanding the Admin Dashboard](#understanding-the-admin-dashboard)
4. [Posting a Job](#posting-a-job)
5. [Managing Job Postings](#managing-job-postings)
6. [Reviewing Applicants](#reviewing-applicants)
7. [Understanding Match Scores](#understanding-match-scores)
8. [Shortlisting Candidates](#shortlisting-candidates)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)
11. [FAQs](#faqs)

---

## Getting Started

### What is Hirely Admin Portal?

The Hirely Admin Portal is your recruitment command center. It allows you to:
- Post and manage job openings
- Review AI-matched candidates
- Access applicant resumes
- Shortlist top candidates
- Track application metrics

### Key Features for Admins

- 🎯 **Smart Candidate Matching** - AI ranks applicants by compatibility
- 📊 **Match Score Analytics** - See how well candidates fit your requirements
- 📄 **Resume Access** - View and download applicant resumes
- ✏️ **Job Management** - Edit, activate, or deactivate postings
- 🔒 **Secure & Isolated** - Your jobs and applicants are private to your account
- 👥 **Shortlist Management** - Organize top candidates

---

## Creating Your Admin Account

### Step 1: Access Admin Registration

1. Go to the Hirely homepage
2. Navigate to `/admin_register` URL
3. Or click "Admin Registration" link (if available)

### Step 2: Company Information

You'll need to provide:

#### Account Credentials
- **Username** - Your admin username (unique)
- **Email Address** - Company email (used for login)
- **Password** - Strong password (minimum 8 characters)
- **Confirm Password** - Must match password

#### Company Details
- **Company Name** - Full legal name of your organization
  - Example: "Hirely Solutions Inc."
  - This appears on all your job postings
  
- **Company Address** - Full business address
  - Include street, city, state/province, postal code
  - Example: "123 Business St, Tech City, CA 94000"

### Step 3: Submit Registration

1. Review all information for accuracy
2. Ensure passwords match
3. Click **"Create Admin Account"**
4. Wait for confirmation message
5. You'll be redirected to the login page

**Important Notes:**
- Only one admin account may be allowed per system (check with your administrator)
- Company name will be visible to all job seekers
- Use a professional company email

### Step 4: First Login

1. Go to the login page
2. Enter your admin email
3. Enter your password
4. Click **"Log In"**
5. You'll be directed to the Admin Dashboard

---

## Understanding the Admin Dashboard

### Dashboard Layout

After logging in, you'll see your **Admin Dashboard** with several sections:

#### Header Navigation
- **Hirely Logo** - Return to dashboard
- **Company Name** - Your organization
- **User Avatar** - Your initials
- **Dropdown Menu:**
  - Profile
  - Logout

#### Left Sidebar

**Profile Card:**
- Your avatar (initials)
- Your full name
- Role: "Administrator"

**Menu Options:**
- **➕ Post a Job** - Create new job posting
- **📋 Jobs Posted** - View all your jobs
- **📊 Reports** - Analytics (if enabled)

#### Main Content Area

**Jobs You Posted Table:**

Displays all your job postings with columns:
- **Role** - Job title
- **Applications** - Number of applicants
- **Status** - Active/Inactive
- **Actions** - Edit, View Applicants, Delete

### Understanding Job Status

- **Active** 🟢 - Job is visible to candidates, accepting applications
- **Inactive** 🔴 - Job is hidden, not accepting applications

---

## Posting a Job

### Accessing the Job Post Form

**Method 1:** From Dashboard
1. Click **"➕ Post a Job"** in the sidebar

**Method 2:** Direct Navigation
1. Navigate to `/post_job` URL

### Job Posting Form Fields

#### 1. Job Title / Role *
**Purpose:** The position you're hiring for

**Examples:**
- "Senior Software Engineer"
- "Marketing Manager"
- "Data Analyst"
- "Customer Success Representative"

**Tips:**
- Use clear, standard job titles
- Avoid internal jargon
- Be specific (e.g., "Senior" vs "Junior")

---

#### 2. Responsibilities *
**Purpose:** What the candidate will do day-to-day

**What to Include:**
- Daily tasks and duties
- Key deliverables
- Team collaboration requirements
- Projects they'll work on

**Example:**
```
- Design and develop scalable web applications using React and Node.js
- Collaborate with product team to define technical requirements
- Conduct code reviews and mentor junior developers
- Participate in agile sprint planning and retrospectives
- Optimize application performance and troubleshoot issues
```

**Tips:**
- Use bullet points for clarity
- Start with action verbs (Design, Develop, Manage, Lead)
- Be specific about technologies/tools
- Include collaboration aspects

---

#### 3. Requirements *
**Purpose:** Must-have qualifications and skills

**What to Include:**
- Technical skills required
- Years of experience needed
- Specific tools or technologies
- Hard requirements (not nice-to-haves)

**Example:**
```
- 5+ years of experience in full-stack web development
- Proficiency in JavaScript, React, Node.js, and MongoDB
- Strong understanding of RESTful APIs and microservices
- Experience with Git version control
- Bachelor's degree in Computer Science or equivalent experience
```

**Tips:**
- Separate must-haves from nice-to-haves
- Be realistic about requirements
- Include specific technical skills
- Mention experience level clearly

---

#### 4. Qualifications *
**Purpose:** Educational background and certifications

**What to Include:**
- Required education level
- Preferred degrees or majors
- Relevant certifications
- Professional licenses

**Example:**
```
- Bachelor's degree in Computer Science, Software Engineering, or related field
- Master's degree preferred but not required
- AWS Certified Solutions Architect (preferred)
- Relevant professional certifications in web development
```

**Tips:**
- Distinguish between required and preferred
- Include equivalent experience clauses
- Mention specific certifications if critical
- Be flexible where possible

---

#### 5. Description *
**Purpose:** Overall job summary and company pitch

**What to Include:**
- Company overview
- Role summary
- Why this job is exciting
- Company culture highlights
- Growth opportunities
- Benefits (if applicable)

**Example:**
```
Join Hirely Solutions Inc., a fast-growing AI recruitment platform revolutionizing 
how companies find talent. We're seeking a Senior Software Engineer to help build 
the next generation of intelligent matching algorithms.

As part of our engineering team, you'll work on challenging problems in machine 
learning, natural language processing, and scalable web architecture. We offer a 
collaborative environment, competitive compensation, and opportunities to work 
with cutting-edge technology.

Our stack includes React, Node.js, Python, and ChromaDB. We value innovation, 
continuous learning, and work-life balance.
```

**Tips:**
- Start with company value proposition
- Highlight unique aspects of the role
- Mention growth opportunities
- Keep it engaging but professional
- Avoid excessive marketing language

---

### Submitting Your Job Post

1. **Fill all required fields** (marked with *)
2. **Review for accuracy** - Check spelling and details
3. **Preview if available** - See how it looks to candidates
4. **Click "Post Job"**
5. **Wait for confirmation** - You'll see a success message
6. **Redirected to dashboard** - Job appears in your list

### After Posting

Your job will:
- ✅ Appear in your "Jobs Posted" list
- ✅ Be set to "Active" status automatically
- ✅ Be visible to all registered job seekers
- ✅ Start receiving applications immediately
- ✅ Be analyzed by AI for candidate matching

---

## Managing Job Postings

### Viewing All Your Jobs

From the Admin Dashboard:
- See all jobs in the main table
- View application counts
- Check active/inactive status
- Access quick actions

### Editing a Job

**Steps:**
1. Find the job in your dashboard table
2. Click **"Edit"** in the Actions column
3. Modify any field you want to change
4. Click **"Update Job"**
5. Changes are saved immediately

**What You Can Edit:**
- Job title/role
- Responsibilities
- Requirements
- Qualifications
- Description
- Active/Inactive status

**Tips:**
- Edit jobs to improve candidate quality
- Update requirements based on applicant feedback
- Clarify ambiguous sections
- Add missing technical skills

### Activating/Deactivating Jobs

**To Deactivate a Job:**
1. Click **"Edit"** on the job
2. Change status to "Inactive"
3. Save changes

**Effects of Deactivation:**
- Job no longer visible to new candidates
- Existing applications remain accessible
- Job stays in your dashboard
- Can be reactivated anytime

**To Reactivate:**
1. Edit the job
2. Change status to "Active"
3. Save changes

### Deleting a Job

**⚠️ Warning:** Deletion is permanent and cannot be undone!

**Steps:**
1. Find the job in dashboard
2. Click **"Delete"** button
3. Confirm deletion in popup
4. Job and all associated applications are removed

**When to Delete:**
- Position has been filled
- Job posting was created in error
- Role is no longer needed
- Consolidating duplicate postings

**Best Practice:** Consider deactivating instead of deleting to preserve application history.

---

## Reviewing Applicants

### Accessing Applicants

**Method 1: From Dashboard**
1. Find the job in your table
2. Click **"View Applicants"** or the application count number
3. See list of all applicants for that job

**Method 2: Direct Access**
1. Navigate to job-specific applicant page
2. View sorted list of candidates

### Applicant List View

For each applicant, you'll see:
- **Candidate Name** - Full name
- **Email** - Contact email
- **Match Score** - AI-calculated compatibility (0-100%)
- **Application Date** - When they applied
- **Resume** - Link to view/download
- **Shortlist Status** - Whether you've shortlisted them

### Sorting Applicants

Applicants are automatically sorted by:
1. **Match Score** (highest first)
2. **Application Date** (most recent)

This helps you quickly identify top candidates.

### Viewing Resumes

**To View a Resume:**
1. Click **"View Resume"** link next to applicant name
2. Resume opens in browser (PDF viewer)
3. You can download or print from there

**Resume Access:**
- ✅ Only you can view resumes for your jobs
- ✅ Secure access through authentication
- ✅ Resumes are stored safely on the server

---

## Understanding Match Scores

### What is a Match Score?

A match score (0-100%) indicates how well a candidate's profile aligns with your job requirements. Higher scores mean better matches.

### How Scores Are Calculated

Hirely uses a sophisticated **hybrid matching algorithm**:

#### 1. Semantic Similarity (70% weight)
- Uses AI to understand meaning and context
- Compares candidate's experience with job requirements
- Recognizes synonyms and related terms
- Example: Matches "software developer" with "software engineer"

#### 2. BM25 Keyword Matching (30% weight)
- Analyzes specific keywords and phrases
- Weights important technical terms higher
- Matches exact skills and technologies
- Example: Direct matches for "Python," "React," "AWS"

### What Influences Match Scores

**High Scores (80-100%):**
- Candidate has most/all required skills
- Experience level matches requirements
- Education aligns with qualifications
- Technical skills are directly relevant
- Resume uses terminology from job description

**Medium Scores (50-79%):**
- Candidate has some required skills
- Partial experience alignment
- Some education/qualification match
- Related but not exact technical skills

**Low Scores (0-49%):**
- Significant skill gaps
- Misaligned experience level
- Different field or industry
- Few matching keywords

### Using Match Scores Effectively

**✅ DO:**
- Use scores as a screening tool
- Review high-scoring candidates first
- Consider candidates 60% and above
- Read resumes even for moderate scores
- Look for potential and transferable skills

**❌ DON'T:**
- Rely solely on match scores
- Ignore candidates below 70%
- Expect 100% matches for every job
- Discard resumes without reading
- Use scores as the only decision factor

**Pro Tip:** A 65% match with great soft skills may be better than an 85% match with poor communication abilities. Always review the full profile!

---

## Shortlisting Candidates

### What is Shortlisting?

Shortlisting helps you organize and track your top candidates for each position. It's a way to mark candidates you want to interview or consider further.

### How to Shortlist

**Method 1: From Applicant List**
1. View applicants for a job
2. Click **"Shortlist"** button next to candidate name
3. Candidate is marked as shortlisted

**Method 2: After Resume Review**
1. View candidate's resume
2. Click **"Shortlist Candidate"** button
3. Return to applicant list to see shortlist status

### Viewing Shortlisted Candidates

**Filter View:**
- Some systems allow filtering to show only shortlisted candidates
- Look for "Shortlisted" filter or tab

**Visual Indicators:**
- Shortlisted candidates have special badge or highlight
- May appear at top of applicant list
- Different background color or icon

### Un-shortlisting

To remove from shortlist:
1. Find the shortlisted candidate
2. Click **"Remove from Shortlist"** or similar
3. Candidate returns to regular applicant pool

### Shortlist Best Practices

**Recommended Process:**
1. **First Pass:** Review all applicants, shortlist those above 60% match
2. **Second Pass:** Read shortlisted resumes in detail
3. **Third Pass:** Narrow down to top 5-10 candidates
4. **Final Step:** Contact shortlisted candidates for interviews

**Shortlist Size Guidelines:**
- **Entry-level roles:** 10-15 candidates
- **Mid-level roles:** 5-10 candidates
- **Senior roles:** 3-7 candidates

---

## Best Practices

### Writing Effective Job Descriptions

#### 1. Be Specific About Requirements
❌ **Vague:** "Experience with programming languages"  
✅ **Specific:** "3+ years experience with Python and JavaScript"

❌ **Vague:** "Good communication skills"  
✅ **Specific:** "Ability to present technical concepts to non-technical stakeholders"

#### 2. Use Industry-Standard Terms
- Use common job titles (helps SEO and candidate search)
- Include technical keywords candidates will search for
- Mention specific tools, frameworks, and technologies
- Use standard acronyms (API, SQL, AWS, etc.)

#### 3. Structure for Readability
- Use bullet points instead of long paragraphs
- Break content into clear sections
- Start bullet points with action verbs
- Keep sentences concise

#### 4. Be Realistic
- Don't list every skill you can think of
- Focus on must-haves vs nice-to-haves
- Consider experience level carefully
- Avoid unicorn hunting (unrealistic combination of skills)

#### 5. Sell the Role
- Highlight exciting projects or technologies
- Mention growth opportunities
- Include company culture highlights
- Be honest but positive

---

### Optimizing for Better Matches

#### Improve Match Quality

**Problem:** Getting low-quality matches?

**Solutions:**
1. **Add more specific technical keywords** to requirements
2. **Clarify experience level** (Junior, Mid, Senior)
3. **Include both common and technical terms**
   - Example: "Machine Learning (ML)" not just "ML"
4. **List specific tools and frameworks**
5. **Update job description** based on applicant feedback

#### Keyword Optimization

The AI matches based on terminology. Include:
- **Programming languages:** Python, Java, JavaScript, C++
- **Frameworks:** React, Angular, Django, Spring
- **Tools:** Git, Docker, Kubernetes, Jenkins
- **Platforms:** AWS, Azure, Google Cloud
- **Databases:** MySQL, PostgreSQL, MongoDB
- **Methodologies:** Agile, Scrum, DevOps
- **Soft skills:** Leadership, Communication, Problem-solving

---

### Managing Application Volume

#### High Volume (50+ applications)

**Strategies:**
1. **Use match scores** to filter to top 30%
2. **Set minimum match threshold** (e.g., only review 70%+)
3. **Quick-scan resumes** of high matches first
4. **Batch process** - review in groups of 10
5. **Shortlist generously** in first pass, narrow later

#### Low Volume (< 10 applications)

**Strategies:**
1. **Review all applicants** regardless of match score
2. **Consider lower match scores** (50%+)
3. **Update job description** to be more appealing
4. **Broaden requirements** if too restrictive
5. **Check if job is set to Active**
6. **Share job posting** externally

---

### Interview Process Tips

#### Preparing for Interviews

After shortlisting:
1. **Review resumes in detail**
2. **Prepare role-specific questions**
3. **Note unique aspects** of each candidate
4. **Plan technical assessments** if needed
5. **Coordinate with your team**

#### Contacting Candidates

Best practices:
- ✅ Respond within 1-2 weeks of application
- ✅ Use professional email template
- ✅ Clearly state next steps
- ✅ Provide interview time options
- ✅ Include company information/location

#### Follow-up

- Set calendar reminders for candidate follow-ups
- Keep communication professional and timely
- Inform rejected candidates politely
- Build a talent pipeline for future roles

---

## Troubleshooting

### Login Issues

**Problem:** Cannot access admin dashboard

**Solutions:**
- Verify you registered as admin (not regular user)
- Check email and password are correct
- Ensure Caps Lock is off
- Clear browser cookies and cache
- Try different browser

---

### Job Posting Issues

**Problem:** Job post fails to submit

**Solutions:**
- Ensure all required fields (*) are filled
- Check for maximum character limits
- Remove any special formatting from text
- Try shorter descriptions
- Check internet connection

**Problem:** Job not appearing to candidates

**Solutions:**
- Verify job status is "Active"
- Check that job was successfully posted
- Refresh the dashboard
- Wait a few minutes for system update
- Re-post if necessary

---

### Applicant Review Issues

**Problem:** Cannot view applicant resumes

**Solutions:**
- Ensure you're logged in as admin
- Verify the applicant applied to YOUR job
- Check that applicant uploaded a resume
- Try different browser
- Ensure PDF viewer is enabled

**Problem:** No applicants for a job

**Possible Reasons:**
- Job requirements too specific/restrictive
- Job recently posted (give it time)
- Limited candidate pool in that skill area
- Job not attractive enough (review description)
- System issue (check with administrator)

---

### Match Score Issues

**Problem:** All match scores are very low

**Solutions:**
- Review job requirements for realism
- Add more common/standard keywords
- Broaden requirements slightly
- Check if required skills are too niche
- Consider if role is entry-level but requirements are senior-level

**Problem:** Match scores seem inaccurate

**Remember:**
- Scores are guides, not perfect predictions
- Algorithm weighs different factors
- Candidate's resume quality affects scoring
- Manual review is still essential

---

## FAQs

### Account & Access

**Q: Can I have multiple admin accounts?**  
A: This depends on system configuration. Check with your administrator.

**Q: Can I change my company name after registration?**  
A: Yes, usually through profile settings. Update carefully as it appears on all your jobs.

**Q: What if I forget my password?**  
A: Use password reset feature (if available) or contact system administrator.

**Q: Can multiple people access the same admin account?**  
A: Not recommended for security reasons. Each recruiter should have their own account.

---

### Job Management

**Q: How many jobs can I post?**  
A: Typically unlimited, but check with your system administrator.

**Q: Can I duplicate a job posting?**  
A: Currently, you need to manually create new postings. Copy content from existing jobs if similar.

**Q: How long do job postings stay active?**  
A: Indefinitely until you deactivate or delete them.

**Q: Can I schedule a job to post later?**  
A: This feature may not be available. Post and set to inactive, then activate when ready.

---

### Applicants & Resumes

**Q: How do I contact applicants?**  
A: Use the email provided in their profile. Direct messaging within the platform may not be available.

**Q: Can I download all resumes at once?**  
A: Currently, resumes must be downloaded individually.

**Q: What if an applicant's resume is missing?**  
A: Contact the applicant directly to request it, or note in your system they didn't upload one.

**Q: Do applicants see their match scores?**  
A: Yes, applicants can see how well they match your job postings.

---

### Match Scores & Algorithm

**Q: Can I adjust the matching algorithm?**  
A: No, the algorithm is standardized across the platform.

**Q: Why do some candidates have 0% match?**  
A: Significant mismatch between their profile and your requirements, or missing resume data.

**Q: Do match scores update if I edit a job?**  
A: Yes, existing applicant scores may recalculate based on new requirements.

**Q: Should I only interview high match scores?**  
A: No, use scores as one factor among many. Great candidates may have moderate scores.

---

### Best Practices

**Q: What's the ideal job description length?**  
A: Detailed enough to be clear, but concise. Aim for 300-600 words total across all fields.

**Q: Should I list salary information?**  
A: This is optional. Many find it helps attract serious candidates and saves time.

**Q: How quickly should I respond to applicants?**  
A: Ideally within 1-2 weeks. Faster response improves candidate experience.

**Q: What's a good match score threshold for interviews?**  
A: Generally 60% and above, but this varies by role and applicant volume.

---

## Admin Dashboard Features Summary

### Quick Reference

| Feature | Location | Purpose |
|---------|----------|---------|
| Post New Job | Sidebar → "Post a Job" | Create job posting |
| View Jobs | Dashboard main area | See all your jobs |
| Edit Job | Actions column → "Edit" | Modify job details |
| Delete Job | Actions column → "Delete" | Remove job permanently |
| View Applicants | Actions column → "View Applicants" | See candidates |
| View Resume | Applicant list → "View Resume" | Access candidate resume |
| Shortlist | Applicant list → "Shortlist" | Mark top candidates |
| Profile | Top right dropdown → "Profile" | Update your info |
| Logout | Top right dropdown → "Logout" | Sign out securely |

---

## Security & Privacy

### Data Security

**Your data is protected through:**
- ✅ Secure authentication and sessions
- ✅ Role-based access control
- ✅ Encrypted password storage
- ✅ Isolated admin accounts (you only see your jobs)
- ✅ Secure resume storage

### Privacy Guidelines

**As an admin, you should:**
- ✅ Only access applicant data for legitimate recruitment purposes
- ✅ Store candidate information securely
- ✅ Comply with data protection regulations (GDPR, etc.)
- ✅ Delete candidate data when no longer needed
- ✅ Use professional email for candidate communication

**Never:**
- ❌ Share applicant information with third parties without consent
- ❌ Use candidate data for purposes other than recruitment
- ❌ Share your admin login credentials
- ❌ Access applicant resumes from jobs you didn't post

---

## Success Metrics

### Track Your Recruiting Performance

**Key Metrics to Monitor:**
- **Application Rate:** Applications per job posting
- **Quality of Match:** Average match score of applicants
- **Time to Shortlist:** Days from posting to shortlist
- **Interview Rate:** Shortlisted candidates / total applicants
- **Response Time:** Your time to review applications

**Improving Performance:**
- Higher avg match scores = better job descriptions
- More applications = more attractive postings
- Faster response = better candidate experience

---

## Getting Help

### Support Resources

**Documentation:**
- This Admin Guide
- User Guide (to understand candidate experience)
- Technical Documentation
- API Documentation (if using integrations)

**Contact:**
- System Administrator
- Technical Support
- Platform Documentation

### Reporting Issues

If you encounter problems:
1. Document what happened
2. Take screenshots
3. Note error messages
4. Record steps to reproduce
5. Contact support with details

---

## Conclusion

The Hirely Admin Portal streamlines your recruitment process through AI-powered candidate matching. By following the best practices in this guide, you'll:

- ✅ Post effective job descriptions
- ✅ Attract quality candidates
- ✅ Efficiently review applicants
- ✅ Make data-driven hiring decisions
- ✅ Build a strong talent pipeline

**Remember:**
- Match scores are tools, not replacements for judgment
- Quality job descriptions lead to quality candidates
- Timely communication improves candidate experience
- Regular review and updates keep your pipeline active

Happy recruiting! 🎯

---

**Document Version:** 1.0  
**Last Updated:** December 3, 2025  
**For Technical Support:** Contact your system administrator  
**Feedback:** Help us improve this guide by reporting unclear sections or suggesting additions
