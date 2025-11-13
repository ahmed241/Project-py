import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import fs from 'fs/promises';

const execAsync = promisify(exec);

// Define the request body type
interface TransportationRequest {
  costMatrix: number[][];
  supply: number[];
  demand: number[];
  problemType: 'min' | 'max';
  solutionType: 'initial' | 'final' | 'both';
  outputType: 'video' | 'pdf' | 'direct';
}

export async function POST(request: NextRequest) {
  try {
    // Parse request body
    const body: TransportationRequest = await request.json();
    
    // Validate input
    if (!body.costMatrix || !body.supply || !body.demand) {
      return NextResponse.json(
        { error: 'Invalid input data' },
        { status: 400 }
      );
    }

    // Create a temporary file with the input data
    const inputData = {
      costMatrix: body.costMatrix,
      supply: body.supply,
      demand: body.demand,
      problemType: body.problemType,
      solutionType: body.solutionType, // Pass this to the Python script
      outputType: body.outputType
    };

    // Generate unique filename for this request
    const timestamp = Date.now();
    const inputFilePath = path.join(process.cwd(), 'temp', `transport_input_${timestamp}.json`);
    const outputDir = path.join(process.cwd(), 'public', 'outputs');
    
    // Ensure directories exist
    await fs.mkdir(path.join(process.cwd(), 'temp'), { recursive: true });
    await fs.mkdir(outputDir, { recursive: true });

    // Write input data to file
    await fs.writeFile(inputFilePath, JSON.stringify(inputData, null, 2));

    // Path to the chosen Python script
    const pythonScriptPath = path.join(process.cwd(), '..', 'backend', 'Transportation', 'transportation_main.py');
    
    // Execute Python script based on output type
    let command: string;
    let outputFile: string;
    const outputTypeForCommand = (body.outputType === 'video' || body.outputType === 'pdf') ? body.outputType : 'direct';

    switch (body.outputType) {
      case 'video':
        outputFile = path.join(outputDir, `transport_${timestamp}.mp4`);
        break;
      case 'pdf':
        outputFile = path.join(outputDir, `transport_${timestamp}.pdf`);
        break;
      default: // 'direct'
        outputFile = path.join(outputDir, `transport_${timestamp}.json`);
        break;
    }
    
    command = `python "${pythonScriptPath}" --input "${inputFilePath}" --output "${outputFile}" --type ${outputTypeForCommand}`;

    console.log('Executing:', command);

    // Execute the Python script
    const { stdout, stderr } = await execAsync(command, {
      timeout: 300000 * 3, // 5 minutes timeout
      env: { ...process.env, "PYTHONIOENCODING": "utf-8" } // Fix for Windows encoding errors
    });

    if (stderr && !stderr.includes('UserWarning')) {
      console.error('Python stderr:', stderr);
    }

    console.log('Python stdout:', stdout);

    // Read the result based on output type
    let result: any;

    if (body.outputType === 'direct') {
      // Read JSON result for direct solution
      const resultData = await fs.readFile(outputFile, 'utf-8');
      result = JSON.parse(resultData);
    } else {
      // For video and PDF, return the file URL
      const fileName = path.basename(outputFile);
      result = {
        url: `/outputs/${fileName}`,
        message: `${body.outputType === 'video' ? 'Video' : 'PDF'} generated successfully`
      };
    }

    // Clean up input file
    await fs.unlink(inputFilePath).catch(() => {});

    // Return response based on output type
    if (body.outputType === 'video') {
      return NextResponse.json({
        success: true,
        videoUrl: result.url,
        message: result.message
      });
    } else if (body.outputType === 'pdf') {
      return NextResponse.json({
        success: true,
        pdfUrl: result.url,
        message: result.message
      });
    } else {
      return NextResponse.json({
        success: true,
        solution: result,
        message: 'Solution calculated successfully'
      });
    }

  } catch (error) {
    console.error('Error processing transportation problem:', error);
    
    return NextResponse.json(
      { 
        error: 'Failed to process transportation problem',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

// Optional: GET endpoint to check API status
export async function GET() {
  return NextResponse.json({
    status: 'ok',
    message: 'Transportation solver API is running',
    endpoints: {
      solve: 'POST /api/transportation/solve'
    }
  });
}