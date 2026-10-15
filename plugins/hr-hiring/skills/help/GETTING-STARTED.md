# Welcome to HR Hiring

This plugin gives you two helpers:

1. **JD Builder** writes a job description for you.
2. **Resume Screener** checks CVs against a job description and tells you who to call.

You only type a command. Everything else is set up for you. If your computer asks for permission the first time, click **Allow**.

## Write a job description

1. Type `/hr-hiring:jd-builder` and then the role, in your own words.
   - Example: `/hr-hiring:jd-builder Sales Manager, Mumbai, 5 years, must know Salesforce`
2. Name anything the JD must have:
   - tools and skills
   - years of experience
   - city

   Everything you name will be in the JD.
3. Wait while it works.
   - It researches the role first, so it takes some time.
   - It asks you something only if your request is unclear or it needs your decision.
4. The Word file opens by itself when it is ready. Read it and edit anything you like.

## Screen CVs

1. Type `/hr-hiring:resume-screener`
2. Share two things:
   - the job description: attach the file, or paste the text
   - the CVs: attach the files, a folder or a zip (PDF or Word)
3. Optional: add what matters to you that the JD doesn't say.
   - Example: "We prefer people who have sold to small businesses."
4. Check the scoring plan it shows you.
   - Change anything you want.
   - Set the pass mark.
   - Say "go".
5. Wait a few minutes. In testing, 5 CVs took about 5 minutes.
6. Read the results table. For each candidate it shows:
   - score
   - Go or No-go
   - reasons for and against
   - questions to ask in the interview
7. Change any decision by saying so.
   - Example: "Move C04 to Go, they were referred."
   - Your reason is saved.
8. Want to know why someone got their score? Just ask.
   - Example: "Why did C04 get this score?"
9. At the end it asks whether to delete the CVs. Say yes unless you still need them.

## Good to know

- The final decision is always yours.
- CVs stay on your computer. Nothing is uploaded.
- Names, age, gender and other personal details are hidden before scoring.
- Career gaps never count against anyone.
- Your files are saved for you. To find one, ask: "Where is my JD?" or "Open my results."

To see this guide again, type `/hr-hiring:help`
