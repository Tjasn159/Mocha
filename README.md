# Mocha
A minimalist, peer-to-peer blogging and social networking platform inspired by the principles of Diaspora and the decentralized nature of the web.

# 📘 Project Overview – Distributed Social Networking Web App

This project is a **federated social networking platform** that allows authors across independent servers (nodes) to interact through a RESTful API.

Our platform enables decentralized communication of posts, comments, and follow requests between local and remote authors, supporting core social media features while preserving node independence.

---

## ⚙️ Core Features

### 🔐 Author Management
- Authors are uniquely identified by UUIDs  
- Each author can customize their profile  
- Authentication is handled locally (no third-party login)

---

### 📝 Posts
- Support for `text/plain` and `text/markdown` content  
- Image posts are base64-encoded and federated across nodes  
- Visibility options: `PUBLIC`, `FRIENDS`, `UNLISTED`, `PRIVATE`

---

### 📬 Inbox System
Each author has an `/inbox/` endpoint that receives:
- Posts (local and foreign)  
- Comments  
- Follow requests  
- Likes  

Posts sent via the inbox are automatically parsed and stored as local or foreign entities.

---

### 👥 Follow System
- Authors can follow other authors (local or remote)  
- Follower data is stored and accessible through `/followers/`  
- Remote follow requests are sent via POST to the recipient’s inbox

---

### 🌐 Federation
- Supports inter-node interaction using REST API calls  
- Public posts are automatically sent to known nodes  
- Handles foreign authors, posts, and comments with appropriate models (`ForeignAuthor`, `ForeignPost`, etc.)  
- Accepts and processes incoming content using a shared federation protocol

## Resources
- Promtional Video
<a href="https://www.youtube.com/watch?v=viOFeeVYwWs">
  <img src="https://github.com/Tjasn159/Mocha/blob/main/w25-project-mod-mocha-main/app/static/authors/images/Screenshot%20(59).png" width="500">
</a>

