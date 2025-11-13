import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import fs from 'fs/promises';

const execAsync = promisify(exec);

export async function POST(request: NextRequest) {
  // 1. Parse the request body
  const body = await request.json();
  const { latex, operation, outputType } = body;

  // 2. Define file paths
  const timestamp = Date.now();
  const tempDir = path.join(process.cwd(), 'temp');
  const outputDir = path.join(process.cwd(), 'public', 'outputs');
  
  // Determine the correct file extension for the output
  let fileExtension = '.json';
  if (outputType === 'video') {
    fileExtension = '.mp4';
  } else if (outputType === 'pdf') {
    fileExtension = '.pdf';
  }
  
  const baseFileName = `laplace_${timestamp}`;
  const inputFile = path.join(tempDir, `${baseFileName}.json`);
  const outputFile = path.join(outputDir, `${baseFileName}${fileExtension}`);

  try {
    // 3. Create directories and write temp input file
    await fs.mkdir(tempDir, { recursive: true });
    await fs.mkdir(outputDir, { recursive: true });

    // Write the full payload for the Python script
    await fs.writeFile(inputFile, JSON.stringify({
      latex,
      operation,
      outputType
    }));

    // 4. Define the Python script path (you'll need to create this)
    const pythonScript = path.join(process.cwd(), '..', 'backend', 'Laplace', 'laplace_main.py');

    // 5. Build the command
    const command = `python -X utf8 "${pythonScript}" --input "${inputFile}" --output "${outputFile}" --type ${outputType}`;

    // 6. Execute the Python script
    await execAsync(command, { timeout: 120000 }); // 2 min timeout for Manim

    // 7. Handle successful execution
    
    // If it was a 'direct' run, read the JSON result
    if (outputType === 'direct') {
      const resultJson = await fs.readFile(outputFile, 'utf-8');
      const result = JSON.parse(resultJson); 
      // Assuming 'result' has { status: 'success', result: 'F(s)', steps: [...] }
      return NextResponse.json(result); 
    }

    // If it was 'video' or 'pdf', return the URL
    const finalFileName = `${baseFileName}${fileExtension}`;
    return NextResponse.json({
      success: true,
      [outputType === 'video' ? 'videoUrl' : 'pdfUrl']: `/outputs/${finalFileName}`
    });

  } catch (error: any) {
    // 8. Handle script failure
    console.error('Laplace Script Error:', error.stderr || error.message);

    // Try to read the error JSON that the script *should* have created
    const errorOutputFile = path.join(outputDir, `${baseFileName}.json`);

    try {
      const errorJson = await fs.readFile(errorOutputFile, 'utf-8');
      const result = JSON.parse(errorJson); 
      return NextResponse.json(
        { error: 'Design failed', details: result.message || 'Unknown Python error' },
        { status: 500 }
      );
    } catch (readError) {
      // Failsafe: Python failed AND we couldn't read its error file
      console.error('CRITICAL: Could not read error output file:', readError);
      return NextResponse.json(
        { error: 'Design failed', details: error.stderr || 'Unknown script failure and unable to read output.' },
        { status: 500 }
      );
    }
  } finally {
    // 9. Always clean up the input file
    await fs.unlink(inputFile).catch(() => {});
  }
}

export async function GET() {
  return NextResponse.json({ status: 'Laplace API ready' });
}