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
**b. Design changes**

After asking AI to review my skeleton, it flagged several issues I hadn't considered:

1. **Dual task lists** — both `Pet` and `Scheduler` held separate task lists, 
   meaning tasks added to a pet wouldn't automatically appear in the scheduler. 
   I plan to fix this by having `Scheduler` iterate over pets directly instead 
   of keeping its own copy.

2. **Missing recurrence rule** — `is_recurring` was just a boolean with no 
   information about how often a task repeats. I added a `recurrence_interval` 
   field using `Optional[timedelta]` to fix this.

3. **Unbounded priority** — `priority` was a plain int with no defined range, 
   making `sort_by_priority()` unpredictable. I will constrain it to 1–5 or 
   use an enum.

4. **No conflict window** — `detect_conflicts()` had no way to measure overlap 
   since `Task` had no duration. I plan to add a `duration` field to `Task`.

These changes were suggested by AI review and I agreed with them after thinking 
through how the methods would actually be implemented.


## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?
...
The scheduler considers due time and priority level (1 = highest).
I decided priority mattered most because a pet's medication should 
always come before a walk, regardless of time.

**b. Tradeoffs**

The conflict detector flags any two tasks within 30 minutes of each other,
even if they belong to different pets. This means a task for Buddy and a 
task for Whiskers could conflict, even though one owner could do both. 
This is reasonable because it errs on the side of caution.


- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used Claude to generate the class skeletons, implement the full logic, 
create the demo script, and write the pytest tests. The most helpful 
prompts were ones that included the file context and asked for specific 
behaviors like conflict detection and priority sorting.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

Claude's first skeleton didn't link Scheduler to Owner, meaning tasks 
added to pets wouldn't appear in the schedule. I caught this through AI 
review and confirmed it made sense before accepting the fix. I also ran 
the demo script to verify the output looked correct before committing.
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested that mark_complete() changes is_completed to True, and that 
adding a task to a Pet increases its task count. These are critical 
because everything else depends on tasks being stored and updated correctly.
**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?


I am fairly confident the core logic works based on the passing tests and 
demo output. Edge cases I would test next include recurring task generation, 
removing a pet and checking its tasks are cleared, and tasks due at midnight.
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
