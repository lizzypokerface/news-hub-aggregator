"""
A Python module for generating Geopolitical Economy (GPE) analysis briefings.

This module uses the Poe API to synthesize a mainstream news summary with expert
analysis from a GPE perspective, producing a comprehensive regional briefing.
"""

import os
import openai

# --- Constants ---

POE_API_URL = "https://api.poe.com/v1"
DEFAULT_MODEL = "Gemini-2.5-Pro"  # A strong model for reasoning and synthesis

# The detailed prompt template to be sent to the LLM.
# It includes the framework, instructions, and examples for high-quality output.
_PROMPT_TEMPLATE = """
### **LLM Prompt Start**

You are a top-tier geopolitical analyst operating within the Geopolitical Economy (GPE) framework. Your analytical voice should mirror that of leading critical experts like **Radhika Desai, Michael Hudson, and Ben Norton**. Your task is to synthesize two input documents to produce a concise, insightful GPE briefing.

**INPUTS:**

--- DOCUMENT 1 START (mainstream regional summary) ---
{mainstream_doc}
--- DOCUMENT 1 END ---

--- DOCUMENT 2 START (expert news analysis) ---
{expert_doc}
--- DOCUMENT 2 END ---


**THE GPE FRAMEWORK: YOUR ANALYTICAL LENS**

Synthesize the events from the inputs through this precise GPE lens. Your analysis for each region must be grounded in these principles:

*   **Expose Economic Drivers:** Go beyond political rhetoric. Identify the material, class, and financial interests driving the events. Ask: *Cui bono?* (Who benefits materially?). Is this about resource control, market access, labor exploitation, or financial dominance?
*   **Identify the Core Conflict:** Frame events within the primary global struggle: the US-led unipolar **imperialist** system seeking to maintain dominance vs. the **anti-imperialist** trend of nations (e.g., BRICS+, the Global South) striving for sovereignty, multipolarity, and independent development.
*   **Deconstruct Narratives:** Scrutinize the language used in the mainstream document. Expose the gap between official justifications ("human rights," "rules-based order," "freedom of navigation") and the underlying material objectives. Identify propaganda and hybrid warfare tactics.
*   **Focus on Financial Warfare:** Analyze the role of debt, sanctions, and institutions like the IMF and World Bank. Frame them not as neutral tools, but as weapons of **financial warfare** and **neocolonial control** used to enforce dependency and enable asset stripping. Highlight resistance like **de-dollarization**.
*   **Reveal Systemic Contradictions:** Point out the inherent tensions in the imperial system—e.g., the conflict between funding foreign wars and domestic decay, or demanding a "rules-based order" while unilaterally breaking it.

**ANALYTICAL VOICE AND TONE**

*   **Incisive and Direct:** Use clear, powerful language. Be unafraid to call things what they are: imperialism, debt peonage, propaganda, hybrid war.
*   **Matter-of-Fact:** Present the analysis as a factual description of power dynamics, not as a moral judgment or political opinion. The tone is that of an expert revealing the hidden mechanics of the global system.
*   **Connect to Material Reality:** Every GPE claim must be implicitly or explicitly linked to the material events described in the source documents. Avoid abstract speculation.

**INSTRUCTIONS FOR OUTPUT:**

1.  **Structure:** Your output must be a single Markdown document. For each region, provide only the heading and the GPE summary. Follow this exact format:

    ```markdown
    ## Region Name

    *GPE*: [Insert your newly synthesized GPE summary here]
    ```

2.  **Region Order:** You MUST follow this strict order. Include a section for every region on this list.

    *   Global
    *   China
    *   East Asia
    *   Singapore
    *   Southeast Asia
    *   South Asia
    *   Central Asia
    *   Russia
    *   West Asia (Middle East)
    *   Africa
    *   Europe
    *   Latin America & Caribbean
    *   North America
    *   Oceania

3.  **Content:** The `*GPE*` summary must be a concise, hard-hitting paragraph that directly synthesizes information from both input documents through the GPE lens described above. It must explain the *why* behind the *what*.

---
### **Examples of the Required Analytical Style**

**Example 1: US-China Tensions**
*   **Mainstream Input:** "The U.S. Navy conducted 'freedom of navigation' exercises in the South China Sea to uphold international law."
*   **Required GPE Output:** *GPE*: The US naval exercises are a tool of imperial containment, using military power to try and subordinate a rising economic competitor. This action is not about "international law" but about disrupting China's anti-imperialist development project and preserving US unipolar dominance in the face of a growing multipolar world.

**Example 2: Economic Crisis & IMF Loan**
*   **Mainstream Input:** "Facing a debt crisis, the nation secured an IMF bailout, which requires fiscal reforms to restore stability."
*   **Required GPE Output:** *GPE*: The IMF bailout is an act of financial warfare, not aid. The imposed "fiscal reforms" are a classic tool of neocolonial control, forcing austerity and privatization to facilitate the stripping of national assets by foreign capital. This deepens the nation's dependency, a modern form of debt peonage designed to prevent a sovereign development path.

**Example 3: Political Unrest in the Global South**
*   **Mainstream Input:** "The president resigned following massive protests over alleged election fraud, which were supported by civil society groups."
*   **Required GPE Output:** *GPE*: The political unrest, framed as a pro-democracy movement, was a hybrid warfare campaign to secure the nation's strategic resources. The "civil society groups" were backed by foreign powers whose material interests were threatened by the government's resource nationalism. The narrative of "election fraud" served as a pretext for a coup aimed at reinstalling a government compliant with the imperial core's economic demands.

### **LLM Prompt End**
"""

# --- Private Functions ---


def _get_poe_client(api_key: str) -> openai.OpenAI:
    """Initializes and returns the Poe API client."""
    return openai.OpenAI(
        api_key=api_key,
        base_url=POE_API_URL,
    )


def _construct_full_prompt(mainstream_analysis: str, expert_analysis: str) -> str:
    """Constructs the full prompt by injecting documents into the template."""
    return _PROMPT_TEMPLATE.format(
        mainstream_doc=mainstream_analysis, expert_doc=expert_analysis
    )


def _call_poe_api(client: openai.OpenAI, model: str, prompt: str) -> str:
    """
    Sends the prompt to the Poe API and returns the response content.

    Args:
        client: The initialized Poe API client.
        model: The name of the model to use (e.g., 'Claude-3-Sonnet').
        prompt: The full prompt string to send.

    Returns:
        The content of the LLM's response as a string.

    Raises:
        ConnectionError: If there is an API-specific error.
        RuntimeError: For other unexpected errors during the API call.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=False,  # Get the full response at once
        )
        if response.choices and response.choices[0].message.content:
            return response.choices[0].message.content.strip()
        else:
            raise RuntimeError(
                "Received an empty or invalid response from the Poe API."
            )
    except openai.APIError as e:
        raise ConnectionError(f"Poe API Error: {e}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred during the Poe API call: {e}")


# --- Public Function ---


def generate_gpe_regional_briefing(
    mainstream_analysis: str,
    expert_analysis: str,
    poe_api_key: str = None,
    model: str = DEFAULT_MODEL,
) -> str:
    """
    Generates a GPE regional briefing by synthesizing two analytical documents.

    This function takes a mainstream news summary and a set of expert analyses,
    sends them to a Large Language Model via the Poe API with a specialized
    prompt, and returns a synthesized briefing in Markdown format.

    Args:
        mainstream_analysis: A string containing the mainstream news summary.
        expert_analysis: A string containing the expert GPE analysis sources.
        poe_api_key: Your Poe API key. If not provided, it will try to use the
                     'POE_API_KEY' environment variable.
        model: The Poe model to use for the generation. Defaults to a capable model.

    Returns:
        A string containing the complete, synthesized GPE regional briefing in
        Markdown format.

    Raises:
        ValueError: If the Poe API key is not provided and not found in the
                    environment variables.
        ConnectionError: If there is an issue communicating with the Poe API.
        RuntimeError: For other unexpected errors during the process.
    """
    # --- 1. Get API Key ---
    if not poe_api_key:
        poe_api_key = os.getenv("POE_API_KEY")

    if not poe_api_key:
        raise ValueError(
            "Poe API key not provided. Please pass it as an argument or set the 'POE_API_KEY' environment variable."
        )

    # --- 2. Orchestrate the analysis process ---
    print(f"Initializing Poe client with model '{model}'...")
    client = _get_poe_client(poe_api_key)

    print("Constructing full prompt with provided documents...")
    full_prompt = _construct_full_prompt(mainstream_analysis, expert_analysis)

    print("Sending request to Poe API for GPE analysis... (This may take a moment)")
    briefing = _call_poe_api(client, model, full_prompt)

    print("Successfully received GPE briefing.")
    return briefing


# --- Example Usage ---
if __name__ == "__main__":
    # This block demonstrates how to use the module.
    # It will only run when the script is executed directly.

    # For this example, we'll use placeholder content. In a real scenario,
    # you would read these from your '.md' files.

    # You must have a POE_API_KEY set in your environment variables to run this.
    if not os.getenv("POE_API_KEY"):
        print("\nERROR: POE_API_KEY environment variable not set.")
        print("Please set your API key to run this example:")
        print("export POE_API_KEY='your_key_here'")
    else:
        print("--- GPE Analysis Module Example ---")

        # Placeholder content for demonstration
        mainstream_content = """
        ## Global
        At a virtual BRICS summit, leaders from China and other member nations called for the defense of multilateralism. Tensions between major powers persist, with the US, Japan, and South Korea planning the "Freedom Edge" trilateral military exercise.

        ## West Asia (Middle East)
        The conflict in Gaza has dramatically escalated, with Israel launching a strike in Doha, Qatar, targeting Hamas leaders. The White House stated the strike did not advance U.S. or Israeli goals.
        """

        expert_content = """
        * [`Geopolitical Economy Report` US attacks blow back, uniting China, India, Russia, Iran; encouraging dedollarization]
        * [`Breakthrough News` Godfather of Chinese Hip Hop: Detroit Rapper Speaks Out Against US Propaganda]
        * [`The New Atlas` Deep Dive: From Venezuela to Serbia & Indonesia, NED-Funded Color Revolution Continues Under Trump]
        * [`Breakthrough News` ‘Gaza Riviera’ Plan Glosses Over Genocide With Billionaires’ Paradise]
        * [`AJ+` Colonialism Never Ended – It Just Became Debt]
        """

        try:
            # Call the main public function
            generated_briefing = generate_gpe_regional_briefing(
                mainstream_analysis=mainstream_content, expert_analysis=expert_content
            )

            print("\n--- Generated GPE Regional Briefing ---")
            print(generated_briefing)

            # Optionally, save the output to a file
            with open("gpe_regional_briefing_output.md", "w", encoding="utf-8") as f:
                f.write(generated_briefing)
            print("\nOutput saved to 'gpe_regional_briefing_output.md'")

        except (ValueError, ConnectionError, RuntimeError) as e:
            print(f"\nAn error occurred: {e}")
