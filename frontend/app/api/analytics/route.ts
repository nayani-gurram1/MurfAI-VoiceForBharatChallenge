import { NextResponse } from 'next/server';
import { execSync } from 'child_process';
import path from 'path';

export const revalidate = 0; // Disable caching for real-time live data

export async function GET() {
  try {
    const backendPath = path.resolve(process.cwd(), '..', 'backend', 'src');
    const script = `
import sys, json
sys.path.append(r'${backendPath}')
from database import _get_connection, get_call_analytics
_get_connection()
analytics = get_call_analytics()
print(json.dumps(analytics))
    `.trim();

    const output = execSync(`python -c "${script.replace(/\n/g, '; ')}"`, {
      encoding: 'utf-8',
      cwd: process.cwd(),
    });

    const data = JSON.parse(output.trim());
    return NextResponse.json({ success: true, analytics: data });
  } catch (error: any) {
    return NextResponse.json(
      { success: false, error: error?.message || 'Failed to fetch analytics' },
      { status: 500 }
    );
  }
}
