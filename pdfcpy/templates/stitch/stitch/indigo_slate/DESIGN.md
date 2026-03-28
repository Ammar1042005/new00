# Design System Strategy: The Architectural Workspace

## 1. Overview & Creative North Star: "The Digital Lithograph"
This design system moves away from the cluttered, utility-first aesthetics of traditional PDF tools and toward a philosophy we call **The Digital Lithograph**. 

A PDF is essentially a digital print. Our goal is to treat the UI not as a "wrapper" for a file, but as a high-end, architectural workspace where the document is the hero. We break the "template" look through **intentional negative space**, **tonal layering**, and **asymmetric sidebars** that prioritize focus. By using the high-contrast ratio between the `manrope` display face and the utilitarian `inter` body face, we create an editorial experience that feels authoritative yet breathable.

---

## 2. Colors & Surface Philosophy
The palette is built on a deep, midnight foundation (`#0b1326`) punctuated by a vibrant, electric indigo (`#c0c1ff`). 

### The "No-Line" Rule
**Explicit Instruction:** Do not use 1px solid borders to define sections. Traditional borders create visual noise and "trap" the eye. Instead, boundaries must be defined solely through background color shifts.
*   **The Transition:** A `surface-container-low` sidebar sitting against a `surface` main workspace provides a clean, sophisticated edge without a single line.

### Surface Hierarchy & Nesting
Treat the UI as a series of physical layers—like stacked sheets of vellum.
*   **Level 0 (Base):** `surface` (#0b1326) for the main application background.
*   **Level 1 (Sections):** `surface-container-low` (#131b2e) for persistent sidebars.
*   **Level 2 (Cards/Tools):** `surface-container` (#171f33) for active tool palettes.
*   **Level 3 (Pop-overs):** `surface-bright` (#31394d) for modals or floating tooltips.

### The "Glass & Gradient" Rule
To elevate CTAs beyond the "Standard Bootstrap" look, use a subtle **Signature Gradient** for primary actions. 
*   **Primary CTA:** Transition from `primary_container` (#4b4dd8) at the bottom-left to `primary` (#c0c1ff) at the top-right. 
*   **Glassmorphism:** For floating toolbars, use `surface_container_highest` at 80% opacity with a `backdrop-filter: blur(12px)`.

---

## 3. Typography: Editorial Utility
We pair the geometric sophistication of **Manrope** with the high-legibility precision of **Inter**.

*   **Display & Headlines (Manrope):** Use `display-lg` and `headline-md` for landing pages and tool headers. The wide apertures of Manrope convey a modern, premium feel.
*   **The Workspace (Inter):** All PDF data, labels, and tool metadata use `body-md` and `label-sm`. Inter is selected for its exceptional x-height, ensuring that even at 0.6875rem (`label-sm`), the text remains hyper-readable for document editing.
*   **Contrast as Hierarchy:** Use `on_surface_variant` (#c7c4d8) for secondary labels to create a "recessed" feel, keeping the focus on the primary document text.

---

## 4. Elevation & Depth: Tonal Layering
Traditional shadows are often "dirty." In this system, depth is achieved through light and tint.

*   **Ambient Shadows:** When a workspace element must float (e.g., a floating "Page Reorder" tool), use a shadow with a blur of `24px` and a color derived from `surface_container_lowest` at 40% opacity. Never use pure black.
*   **The "Ghost Border" Fallback:** If high-contrast accessibility is required, use `outline_variant` (#464555) at **15% opacity**. This creates a "suggestion" of a boundary that disappears into the background.
*   **Selection States:** Instead of a thick border, a selected PDF page should be indicated by a `2px` outer glow using `primary` (#c0c1ff) and a subtle background shift to `surface_container_highest`.

---

## 5. Components
### The Utility Toolbar
*   **Style:** `surface_container_high` with a `lg` (0.5rem) corner radius.
*   **Interaction:** Icons should use `on_surface_variant`. On hover, the background shifts to `surface_bright` and the icon transitions to `primary`.

### Primary Buttons
*   **Radius:** `full` (9999px) for a "capsule" look that feels approachable and modern.
*   **Color:** Use the **Signature Gradient** (Primary Container to Primary). 
*   **Text:** `label-md` in `on_primary_fixed` (#07006c) for maximum punch.

### Edit Tool Icons
*   **Consistency:** All icons must use a **2px stroke weight**. Avoid filled icons unless in an "active" state. This mimics the "neat" and "airy" aesthetic of the typeface.

### Sidebars & Lists
*   **The Rule:** **No Dividers.** 
*   **Separation:** Use `spacing-4` (0.9rem) of vertical white space between list items. Use a subtle background change to `surface_container_highest` for the active item.

### Input Fields
*   **Style:** Minimalist. `surface_container_lowest` background with a `sm` (0.125rem) bottom-only accent in `outline_variant`. On focus, the accent transitions to `primary` and grows to 2px.

---

## 6. Do’s and Don’ts

### Do:
*   **Do** use `tertiary` (#ffb695) for "destructive" or "warning" actions like 'Delete Page' or 'Discard Changes' to provide a sophisticated contrast to the indigo.
*   **Do** embrace asymmetry. A wide left sidebar for navigation and a slim right sidebar for metadata creates a dynamic, professional "cockpit" feel.
*   **Do** use the `spacing-16` (3.5rem) for section breathing room. High-end design requires "wasteful" space.

### Don't:
*   **Don't** use 100% black (#000000) for shadows or text. It breaks the "Digital Lithograph" atmosphere.
*   **Don't** use standard "Select" dropdowns. Create custom overlays using the `surface_container_highest` token and `xl` (0.75rem) corner radius.
*   **Don't** use sharp corners. The `md` (0.375rem) and `lg` (0.5rem) radii are the standard for this system to maintain a "soft-professional" tone.