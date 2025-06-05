# Application UI/UX Design

## 1. Overall Design Philosophy

The application's design philosophy centers around creating a user experience that is:

*   **Clean and Intuitive:** The interface will be uncluttered, with a clear visual hierarchy and logical flow, making it easy for users to understand and navigate.
*   **Modern:** A contemporary aesthetic will be employed, utilizing modern UI patterns and components.
*   **Guided:** Especially for new users or complex tasks, the UI will provide guidance through clear instructions, prompts, and feedback, helping users achieve their goals efficiently.
*   **Visual Feedback Focused:** The system will provide immediate and clear visual feedback for user actions, including input validation, loading states, and successful operations.
*   **Direct Manipulation (for Schema):** Users should feel in control by directly interacting with and manipulating the visual representation of their database schema.

## 2. Key Screens (Textual Wireframes/Mockups)

### A. Landing Page / Dashboard

*   **Purpose:** Welcome users, provide an entry point to create new schemas, and allow logged-in users to access existing projects.
*   **Elements:**
    *   **Navigation Bar (Top):**
        *   App Logo and Name (e.g., "SchemaGenius")
        *   Links: "Home", "My Projects" (visible if logged in), "Documentation", "Login/User Profile" (shows user avatar/name if logged in, else "Login/Sign Up").
    *   **Main Content Area:**
        *   **Tagline:** Prominent, clear tagline, e.g., "Intelligently generate database schemas from your code, text, or data."
        *   **Primary Call to Action (CTA):** Large button: "[+] Create New Schema Project"
    *   **Secondary Section (if logged in, below CTA or on a sidebar):**
        *   **Heading:** "My Recent Projects"
        *   **List:** Clickable project names, perhaps with last modified date. (e.g., "Customer Database - 2 days ago", "Blog Schema - 1 week ago").
        *   Link: "View All Projects..." (if list is paginated/truncated).
*   **Layout:**
    *   Centered tagline and main CTA for immediate focus.
    *   Recent projects section easily scannable.
    *   Clean, spacious, and uncluttered to avoid overwhelming the user.

### B. Project Creation / Input Page

*   **URL:** `/project/new` (for new) or `/project/{id}/input` (if editing an existing project's input)
*   **Purpose:** Allow users to name their project and provide the input data for schema generation.
*   **Elements:**
    *   **Page Title/Header:** "Create New Schema Project" or "Edit Project Input: {Project Name}"
    *   **Project Name Input Field:**
        *   Label: "Project Name:"
        *   Input: `[____________________]` (Text field, auto-focused on new project creation)
        *   Validation: Required, character limits.
    *   **Input Method Selector (Tabs or Segmented Control):**
        *   Options: `[ Code Snippet ] [ Text Description ] [ File Upload ]`
    *   **Dynamic Input Area (content changes based on above selector):**
        *   **If "Code Snippet" is selected:**
            *   **Language Selector Dropdown:** "Language: `[ SQL (MySQL) v]`" (Options: SQL (PostgreSQL), Python (SQLAlchemy), Java (JPA), etc.)
            *   **Code Editor Area:** Large text area with syntax highlighting (e.g., using CodeMirror or Monaco Editor). Placeholder text: "// Paste your SQL DDL, Python ORM, or Java JPA code here..."
            *   **Helper Link:** "Show example" (clicking this could open a small modal or expand an inline section showing a relevant code example for the selected language).
        *   **If "Text Description" is selected:**
            *   **Text Area:** Large text area. Placeholder text: "Describe your database needs. For example: 'I need a table for users with fields for name, email, and password. Users can have multiple posts. Each post has a title and content.'"
            *   **Tips/Prompts:** Small text below the area with examples of effective descriptions.
        *   **If "File Upload" is selected:**
            *   **Drag-and-Drop Area / File Input Button:** Large dashed-border area: "Drag your CSV or JSON file(s) here, or [click to browse]."
            *   **File Type Hint:** "Supported formats: .csv, .json."
            *   **Uploaded File List:** (If a file is uploaded or dragged) Displays file name, size, and a remove (X) icon. If multiple files are allowed for a single project (e.g., multiple CSVs representing different tables), this area lists them.
    *   **Target Database Selector (Optional here, can be post-generation):**
        *   Label: "Target Database (Optional):"
        *   Dropdown: `[ Autodetect (if possible) v ]` (Options: MySQL, PostgreSQL, MongoDB, etc.)
    *   **Action Buttons:**
        *   **Primary:** "[ Generate Schema ]" (Button is disabled until a project name is entered and valid input is provided in the selected input area).
        *   **Secondary:** "[ Save Draft ]" (Saves the current input and project name without proceeding to generation).
*   **Layout:**
    *   Project name prominently at the top.
    *   Clear visual separation for the input method selector and its corresponding input area.
    *   The input area itself should be the main focus of the page.

### C. Schema Visualization and Editing Page

*   **URL:** `/project/{id}/schema`
*   **Purpose:** Display the generated schema visually, allow users to inspect, edit, and refine it.
*   **Elements:**
    *   **Navigation/Header:**
        *   Breadcrumbs: "My Projects > {Project Name} > Schema Editor"
        *   Project Name (display)
    *   **Main Area: Visual Schema Editor (Canvas):** (e.g., using React Flow or similar)
        *   Displays tables/collections as distinct nodes (boxes).
        *   Each node shows table name, list of fields/attributes (name, type, PK/FK indicators).
        *   Relationships (lines/curves) connect related fields or tables.
        *   Nodes are draggable.
        *   Context Menus (on right-click of a table or field):
            *   Table: "Edit Table", "Delete Table", "Add Field".
            *   Field: "Edit Field", "Delete Field", "Define as Primary Key", "Add Index".
    *   **Toolbar/Sidebar (Left or Right side, collapsible):**
        *   **Schema Elements Panel:**
            *   Button: "[+] Add Table" (or "Add Collection" for NoSQL)
            *   Tree View or Accordion List:
                *   `Tables`
                    *   `users (id, username, email)`
                    *   `posts (id, title, content, user_id)`
                *   `Relationships`
                    *   `posts.user_id -> users.id`
                *   Clicking an item highlights it in the visual editor and populates the Properties Panel.
        *   **Properties/Edit Panel (dynamically updates based on selection in canvas or tree view):**
            *   **If Table selected:**
                *   Input: "Table Name: `[users_______]`"
                *   (List of fields, each editable or removable)
            *   **If Field selected:**
                *   Input: "Field Name: `[username____]`"
                *   Dropdown: "Data Type: `[ STRING v ]`" (Generic types initially, maps to specific DB types on export)
                *   Checkboxes: "[ ] Primary Key", "[ ] Not Null", "[ ] Unique"
                *   Input: "Default Value: `[___________]`"
            *   **If Relationship selected:**
                *   Dropdowns for source/target tables and fields.
                *   Dropdown for relationship type (one-to-one, one-to-many, many-to-many).
        *   **Validation Status Indicator:**
            *   Text: "Schema Status: Valid" (green) or "Schema Status: 3 Issues Found" (red, clickable to show a list of issues/warnings).
    *   **Action Buttons (Top bar or bottom of sidebar):**
        *   "[ Validate Schema ]" (Manually trigger validation)
        *   "[ Save Changes ]" (Persists modifications)
        *   "[ Export Schema ]" (Opens Export Page/Modal)
*   **Layout:**
    *   The visual canvas should occupy the largest portion of the screen (~70%).
    *   Sidebar/Toolbar provides tools and detailed editing capabilities without obscuring the main view.

### D. Export Page/Modal

*   **Triggered by:** Clicking "Export Schema" button from the Schema Visualization and Editing Page.
*   **Purpose:** Allow users to select the final database system and format for their schema and download/copy it.
*   **Elements:**
    *   **Title:** "Export Schema: {Project Name}"
    *   **Target Database System Selector:**
        *   Label: "Export for:"
        *   Dropdown: `[ PostgreSQL v ]` (Defaults to project setting or last selection. Options: MySQL, PostgreSQL, MongoDB, etc.)
    *   **Export Format Selector (dynamically updates based on Target DB):**
        *   Label: "Format:"
        *   Dropdown: `[ SQL DDL v ]` (Options for SQL: SQL DDL. Options for MongoDB: JSON Schema, etc.)
    *   **Options (Checkboxes, context-dependent):**
        *   (If SQL DDL) "[x] Include `DROP TABLE IF EXISTS` statements"
        *   (If SQL DDL) "[x] Include comments from schema"
        *   (If applicable) "[ ] Generate sample data insertion statements"
    *   **Preview Area (Read-only text area):**
        *   Shows a snippet or the full generated export content. Updates dynamically if options change.
    *   **Action Buttons:**
        *   **Primary:** "[ Download File ]"
        *   **Secondary:** "[ Copy to Clipboard ]"
        *   **Tertiary:** "[ Close ]" or "[ Cancel ]"
*   **Layout:**
    *   Presented as a modal overlay or a dedicated simple page.
    *   Clear, sequential options.
    *   Preview area is crucial for user confidence.
    *   Prominent download/copy buttons.

## 3. User Experience (UX) Flow

### New User - First Schema Creation
1.  **Arrival:** User lands on the **Landing Page**.
2.  **Initiation:** Clicks the "[+] Create New Schema Project" button.
3.  **Input Setup:** Navigates to the **Project Creation/Input Page**.
4.  **Naming:** Enters a "Project Name" (e.g., "My E-commerce App").
5.  **Method Selection:** Selects an input method tab (e.g., "Text Description").
6.  **Provide Input:**
    *   If "Text Description": Types "I need a products table with id, name, price. Also a customers table with id, email. Customers can have many orders. Orders have an order_date and total_amount."
    *   If "Code Snippet": Selects "Language" (e.g., "SQL (PostgreSQL)"), pastes DDL into the code editor.
    *   If "File Upload": Drags a `products.csv` file into the upload area.
7.  **Generation Trigger:** Clicks the "Generate Schema" button.
8.  **Processing Feedback:** A loading indicator (e.g., spinner with "Generating schema...") is displayed.
9.  **Visualization & Editing:** User is taken to the **Schema Visualization and Editing Page**. The generated tables ("products", "customers", "orders") and their inferred fields/relationships are displayed visually.
10. **Exploration & Refinement:**
    *   User examines the visual schema.
    *   Clicks on the "products" table. The Properties Panel shows its details.
    *   User edits the "price" field, changing its data type from "TEXT" (inferred from CSV) to "DECIMAL".
    *   User right-clicks the "customers" table, selects "Add Field", and adds an "address" field of type "STRING".
11. **Validation:** Clicks "Validate Schema". Receives feedback (e.g., "Validation successful" or a list of issues like "Missing primary key on 'orders' table"). User corrects any issues.
12. **Saving:** Clicks "Save Changes". A toast notification confirms "Project saved successfully."
13. **Export Initiation:** Clicks "Export Schema".
14. **Export Configuration:** The **Export Modal/Page** appears.
15. **Format Selection:** User confirms "Target Database" is "PostgreSQL" and "Format" is "SQL DDL".
16. **Output Action:** Clicks "Download File". The SQL DDL script is downloaded to their computer.
17. **Completion:** User closes the modal.

### Returning User - Editing Existing Project
1.  **Arrival & Login:** User lands on the **Landing Page/Dashboard** (already logged in).
2.  **Project Selection:** Clicks on an existing project name (e.g., "My E-commerce App") from the "My Recent Projects" list.
3.  **Direct to Editor:** User is taken directly to the **Schema Visualization and Editing Page** for that project, with the previously saved schema loaded.
4.  **Continued Refinement:** User continues from step 10 in the "New User" flow (e.g., adds a new "reviews" table, modifies relationships, etc.).
5.  **Saving & Exporting:** Follows steps 11-17 as needed.

## 4. Key UI Interactions and Feedback

*   **Real-time Input Validation:**
    *   Project Name: Red border and message if empty or invalid characters.
    *   Code Editor: Syntax highlighting; inline error markers for malformed code.
    *   File Upload: Feedback on incorrect file types or sizes.
*   **Drag and Drop:**
    *   File Upload: Visual change in dropzone area when dragging a file over it.
    *   Schema Editor: Smooth dragging of tables; visual cues for linking relationships.
*   **Tooltips & Hints:**
    *   On hover over icons, buttons with ambiguous labels, or complex settings.
    *   Placeholder text in input fields.
*   **Loading States:**
    *   Global spinner or progress bar during schema generation, validation, or saving.
    *   Button disabled with spinner icon for action-specific loading.
*   **Notifications (Toasts):**
    *   Success: "Project saved.", "Schema exported.", "Copied to clipboard."
    *   Error: "Error generating schema: Invalid SQL syntax.", "Failed to save project."
    *   Warning: "Some relationships could not be automatically inferred."
*   **Contextual Help:**
    *   Small "?" icons or "Learn more" links next to complex features, leading to specific documentation sections or popover explanations.
*   **Disabled States:** Buttons like "Generate Schema" or "Export Schema" are disabled until prerequisite conditions are met (e.g., input provided, schema valid).

## 5. Accessibility Considerations (Briefly)

*   **Keyboard Navigation:** Ensure all interactive elements (buttons, inputs, tabs, visual schema elements) are focusable and operable via keyboard.
*   **Color Contrast:** Use color combinations that meet WCAG AA standards for text, UI components, and visual indicators.
*   **ARIA Attributes:** Implement appropriate ARIA (Accessible Rich Internet Applications) roles, states, and properties for custom controls (e.g., visual schema editor, custom dropdowns) to make them understandable to assistive technologies.
*   **Semantic HTML:** Use semantic HTML5 elements where appropriate to provide inherent meaning and structure.
*   **Focus Management:** Ensure logical focus order and manage focus appropriately when modals or new views appear.
