# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
**a. Initial design**

I designed four classes for PawPal+:

- **Owner** — stores the pet owner's contact info (name, email, phone) 
  and holds a list of their pets. Responsible for adding and removing pets.

- **Pet** — stores an individual animal's details (name, species, breed, age) 
  and holds a list of care tasks. Responsible for managing its own tasks.

- **Task** — represents a single care action like a feeding, walk, medication, 
  or appointment. Tracks the due time, priority, whether it recurs, and 
  whether it has been completed.

- **Scheduler** — the central organizer. Takes all tasks across all pets, 
  sorts them by priority, detects time conflicts, and generates the next 
  occurrence of recurring tasks.
**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
