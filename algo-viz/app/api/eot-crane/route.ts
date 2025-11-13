import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import fs from 'fs/promises';

const execAsync = promisify(exec);

export async function POST(request: NextRequest) {
  const body = await request.json();
  const { load, loadUnit, speed, speedUnit, liftHeight, outputType } = body;

  const timestamp = Date.now();
  const tempDir = path.join(process.cwd(), 'temp');
  const outputDir = path.join(process.cwd(), 'public', 'outputs');

  // --- FIX 1: Determine correct file extension ---
  let fileExtension = '.json';
  if (outputType === 'video') {
    fileExtension = '.mp4';
  } else if (outputType === 'pdf') {
    fileExtension = '.pdf';
  }
  
  const baseFileName = `eot_${timestamp}`;
  const inputFile = path.join(tempDir, `${baseFileName}.json`);
  const outputFile = path.join(outputDir, `${baseFileName}${fileExtension}`);

  try {
    // --- 1. Setup ---
    await fs.mkdir(tempDir, { recursive: true });
    await fs.mkdir(outputDir, { recursive: true });

    await fs.writeFile(inputFile, JSON.stringify({
      load,
      loadUnit,
      speed,
      speedUnit,
      liftHeight,
      outputType 
    }));

    // Path to solver (executing the main script)
    const pythonScript = path.join(process.cwd(), '..', 'backend', 'EOT_Crane', 'eot_main.py');

    // --- 2. Build Command (This is now correct) ---
    // The --output path now has the correct extension (e.g., .mp4)
    const command = `python -X utf8 "${pythonScript}" --input "${inputFile}" --output "${outputFile}" --type ${outputType}`;

    // --- 3. Run Script ---
    await execAsync(command, { timeout: 120000 }); // 2 min timeout

    // --- 4. Handle Success ---
    
    // If it was a 'direct' run, we MUST read the JSON file
    if (outputType === 'direct') {
      const resultJson = await fs.readFile(outputFile, 'utf-8');
      const result = JSON.parse(resultJson); // Will have { status: 'success', results: {...} }
      return NextResponse.json({ success: true, solution: result.results });
    }

    // If it was 'video' or 'pdf', the file itself is the result.
    // We just return the URL to it.
    const finalFileName = `${baseFileName}${fileExtension}`;
    return NextResponse.json({
      success: true,
      [outputType === 'video' ? 'videoUrl' : 'pdfUrl']: `/outputs/${finalFileName}`
    });

  } catch (error: any) {
    // --- 5. Handle Failure ---
    console.error('EOT Crane Script Error:', error.stderr || error.message);

    // If the script fails, it should have created a .json file with the error
    // We need to find *that* file, not the MP4 path.
    const errorOutputFile = path.join(outputDir, `${baseFileName}.json`);

    try {
      const errorJson = await fs.readFile(errorOutputFile, 'utf-8');
      const result = JSON.parse(errorJson); 
      return NextResponse.json(
        { error: 'Design failed', details: result.message },
        { status: 500 }
      );
    } catch (readError) {
      console.error('CRITICAL: Could not read error output file:', readError);
      return NextResponse.json(
        { error: 'Design failed', details: error.stderr || 'Unknown script failure and unable to read output.' },
        { status: 500 }
      );
    }
  } finally {
    // Always try to clean up the input file
    await fs.unlink(inputFile).catch(() => {});
  }
}

export async function GET() {
  return NextResponse.json({ status: 'EOT Crane API ready' });
}