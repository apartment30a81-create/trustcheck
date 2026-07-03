/* =======================================
   TRUSTCHECK — Venice AI Integration Module
   Optional: user provides API key for deeper vision analysis.
   ======================================= */

const VENICE_API = 'https://api.venice.ai/api/v1';

/**
 * Analyze an image using Venice AI vision model.
 * @param {string} apiKey - Venice API key
 * @param {File} file - Image file to analyze
 * @returns {Promise<Object>} Analysis results
 */
export async function analyzeWithVenice(apiKey, file) {
  if (!apiKey) throw new Error('No API key provided');
  if (!file.type.startsWith('image/')) throw new Error('Venice AI analysis requires an image file');

  // Convert file to base64
  const base64 = await fileToBase64(file);
  const mimeType = file.type;

  // Call Venice chat/completions with vision
  const response = await fetch(`${VENICE_API}/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`
    },
    body: JSON.stringify({
      model: 'gemma-3-27b-it',
      messages: [
        {
          role: 'user',
          content: [
            {
              type: 'text',
              text: `You are an expert forensic analyst. Analyze this image for signs of AI generation. 

Examine for:
1. AI generation artifacts (smooth textures, unrealistic lighting, anatomical errors)
2. C2PA/content credential indicators visible in metadata
3. Overall authenticity assessment

Respond in this exact JSON format (no markdown, no code blocks):
{
  "is_ai_generated": true/false,
  "confidence_percent": <0-100>,
  "evidence": [
    {"finding": "...", "severity": "high|medium|low", "explanation": "..."}
  ],
  "summary": "<one sentence summary>"
}`
            },
            {
              type: 'image_url',
              image_url: { url: `data:${mimeType};base64,${base64}` }
            }
          ]
        }
      ],
      temperature: 0.1,
      max_tokens: 1000
    })
  });

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`Venice API error (${response.status}): ${err}`);
  }

  const data = await response.json();
  const text = data.choices?.[0]?.message?.content || '';

  // Parse JSON from response
  try {
    // Try to find JSON in the response (handle markdown wrapping)
    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]);
    }
    throw new Error('Could not parse AI response');
  } catch {
    return {
      is_ai_generated: null,
      confidence_percent: 0,
      evidence: [{ finding: 'Analysis parsing error', severity: 'low', explanation: 'Could not interpret AI response' }],
      summary: 'Analysis failed — please try again'
    };
  }
}

/**
 * Validate a Venice API key by checking account balance.
 */
export async function validateVeniceKey(apiKey) {
  try {
    const response = await fetch(`${VENICE_API}/models`, {
      headers: { 'Authorization': `Bearer ${apiKey}` }
    });
    return response.ok;
  } catch {
    return false;
  }
}

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result;
      const base64 = result.split(',')[1] || result;
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}