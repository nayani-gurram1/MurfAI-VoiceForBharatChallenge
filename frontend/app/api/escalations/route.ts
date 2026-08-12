import { execSync } from "child_process";
import { NextResponse } from "next/server";
import path from "path";

export async function GET() {
  try {
    const backendPath = path.resolve(process.cwd(), "..", "backend", "src");
    const script = `
import sys, json
sys.path.append(r'${backendPath}')
from database import _get_connection, get_open_escalations
_get_connection()
escalations = get_open_escalations()
print(json.dumps(escalations))
    `.trim();

    const output = execSync(`python -c "${script.replace(/\n/g, "; ")}"`, {
      encoding: "utf-8",
      cwd: process.cwd(),
    });

    const data = JSON.parse(output.trim());
    return NextResponse.json({ success: true, escalations: data });
  } catch (error: any) {
    return NextResponse.json(
      { success: false, error: error?.message || "Failed to fetch escalations" },
      { status: 500 }
    );
  }
}
