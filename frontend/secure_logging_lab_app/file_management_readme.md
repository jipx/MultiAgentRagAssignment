# 📁 File Management in Secure Logging Lab App

This document explains how file upload, saving, and reuse are handled in the Streamlit-based Secure Logging Lab App.

---

## 🔄 Lifecycle Overview

### 1. **Initial Startup (First Visit or App Load)**

- At startup, the app runs `init_uploaded_from_data_folder()`.
- It scans the `data/` folder for any matching files:
  - `labnotes_<lab>_<step>.txt`
  - `quiz_<lab>_<step>.json`
  - `solution_<lab>_<step>.txt`
  - `original_<lab>_<step>.txt`
- Found files are stored in `st.session_state.uploaded`, enabling persistent access.

✅ **Result**: Files are preloaded and used across tabs without needing re-upload after refresh.

---

### 2. **User File Upload (Sidebar Uploads)**

- Users can upload:
  - `Labnotes` (.txt)
  - `Quiz` (.json)
  - `Solution` (.txt)
  - `Original` (.txt)
- Uploaded files are saved to the `data/` folder using this format:
  ```
  data/<prefix>_<lab>_<step>.<ext>
  ```
  Example:
  ```
  data/labnotes_lab5_step1.txt
  data/quiz_lab5_step1.json
  ```
- The upload instantly updates `st.session_state.uploaded` for app-wide access.

✅ **Result**: Uploaded content is saved persistently and immediately accessible.

---

### 3. **App Refresh or Redeployment**

- On reload, the app:
  - Checks `st.session_state.uploaded` for cached paths
  - If not available, scans the `data/` folder for matching files
- Content in all app tabs is automatically rehydrated from disk.

✅ **Result**: No need to re-upload files after refresh or deployment.

---

### 4. **Quiz Generation Flow**

- Clicking **"Generate Quiz"**:
  1. Sends Lab Notes to the quiz-generation API
  2. Receives a JSON quiz response
  3. Saves quiz to:
     ```
     data/quiz_<lab>_<step>.json
     ```
  4. Updates `st.session_state.uploaded["quiz"]`
  5. Renders quiz for user interaction

✅ **Result**: Dynamically generated quizzes are persisted and reused.

---

## ✅ File Handling Summary

| Action         | File Source              | Persistent | Notes                                     |
| -------------- | ------------------------ | ---------- | ----------------------------------------- |
| First load     | `data/` folder           | ✅          | Searches for matching filenames           |
| Refresh/reload | `session_state` fallback | ✅          | Reuses existing session or file cache     |
| New upload     | Saved to `data/` folder  | ✅          | Overwrites if same lab/step prefix exists |
| Generate quiz  | Saves API result to file | ✅          | Uses result immediately in quiz tab       |

---

## 🔒 Notes

- File structure is user-agnostic unless scoped by user ID in the future.
- App assumes one set of files per Lab/Step combination.
- Future enhancements can include per-user folders or versioning.

---

For more details on how these files are used in the interface, see `main_app.py` and `lab_tabs.py`.

