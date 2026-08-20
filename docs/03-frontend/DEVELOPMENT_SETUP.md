# Frontend Development Setup

> **Implemented in Step 3:** a React/Vite startup shell with vanilla CSS.
>
> **Planned for later steps:** the INDRA dashboard, maps, charts, scenario UI, recommendations, evidence drawer, and business API calls.

## Windows PowerShell

From the repository root:

```powershell
Set-Location .\frontend
npm install
npm run dev
```

Open `http://localhost:3000`. Vite is explicitly configured for port 3000 so FastAPI's local CORS default matches the frozen API contract.

The future backend base URL is `http://localhost:8000`. No browser API request is implemented in Step 3.
