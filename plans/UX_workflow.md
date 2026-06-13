UI/UX and User Workflow:
	
- There should be a single Dashboard page.
- Show the project title at the top.
- There should be 4 Tabs: Overall (a weighted combination of each category's scores) and one tab for each category (Quantity, Quality, Collaboration).
- In each tab, it should include a brief description (a short definition and its interpretation), the leaderboard (top 5 contributors with highest scores for corresponding category, and one row at the bottom for the average value), and a breakdown section. In the breakdown section, it should show individual descriptions and leaderboards for each sub-category.
Note: Normalize the scores before combining them, using 0.5 for the average score across all contributors.
- Show a loading screen when metrics are being loaded. Display an error message if loading fails
- Tech Stack: React 19, TypeScript, Vite, TanStack Query, Tailwind CSS.
