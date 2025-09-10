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

You are an expert geopolitical analyst specializing in the framework of Geopolitical Economy (GPE). Your task is to create a comprehensive regional briefing by synthesizing information from two source documents.

Your goal is to produce a new document, `gpe-regional-briefing.md`, that appends a GPE analysis to an existing mainstream summary for various world regions.

**INPUTS:**

--- DOCUMENT 1 START (regional-briefing.md) ---
{mainstream_doc}
--- DOCUMENT 1 END ---

--- DOCUMENT 2 START (weekly-news.md) ---
{expert_doc}
--- DOCUMENT 2 END ---


**THE GPE FRAMEWORK FOR YOUR SYNTHESIS:**

When writing the `*GPE*` summary for each region, you must connect the dots between the events described in the mainstream brief and the critical analysis provided by the expert sources. Your synthesis should adhere to these core GPE principles:

*   **Integrate Politics and Economics:** Treat economic events as political and political events as having economic drivers. Reject their artificial separation.
*   **Identify the Core Conflict:** Frame events within the central struggle between **imperialism** (the need for dominant powers to control markets, resources, and labor) and **anti-imperialism** (the struggle by other nations for sovereignty and independent development).
*   **Focus on Material Interests:** Look past the official rhetoric (e.g., "spreading democracy," "national security") to uncover the underlying material and class interests. Ask: *Cui bono?* (Who benefits materially?).
*   **Reveal Contradictions:** Highlight the inherent tensions in the system. For example, the contradiction between an empire's military spending abroad and the declining welfare of its domestic population, or the contradiction between demanding a "rules-based order" while simultaneously violating it.
*   **Connect the Local to the Global:** Show how a local event (e.g., a protest, a factory closure) is connected to the dynamics of the global system.

**INSTRUCTIONS FOR OUTPUT:**

1.  **Structure:** Your output must be a single Markdown document. For each region, you will create a section with the following exact format:

    ```markdown
    ## Region Name

    *mainstream*: [Insert the verbatim summary from regional-briefing.md here]

    *GPE*: [Insert your newly synthesized GPE summary here]
    ```

2.  **Region Order:** You MUST follow this strict order for the regions. Include a section for every region on this list, even if information is sparse.

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

3.  **Content Rules:**
    *   The `*mainstream*` summary must be an exact, unaltered copy of the text from `regional-briefing.md`.
    *   The `*GPE*` summary should be a concise paragraph that synthesizes the information as instructed above. It should provide the "aha!" moment by explaining the underlying dynamics.
    *   If no clear GPE analysis is possible for a region based on the provided sources, you should still include the section and make a best-effort attempt to apply high-level GPE principles to the mainstream facts. If no mainstream summary is available for a region, note that.

4.  **Tone and Language:**
    *   **Objective and Factual:** Present the GPE analysis as a matter-of-fact description of global realities and power relationships.
    *   **Plain Language:** Use clear, straightforward terminology. Avoid academic jargon or overly charged political language. The goal is clarity, not rhetoric.

Your final output should be the complete, combined regional briefing, ready for publication as `gpe-regional-briefing.md`.

---
Here are examples of the thinking process you should apply:

### **Example 1: US-China Tensions**
*   **Mainstream View (Input):** "The U.S. Navy conducted 'freedom of navigation' exercises in the South China Sea to ensure regional stability and uphold international law."
*   **GPE Thinking Process:** The exercises are not a neutral act but a tool of **imperial containment** to hinder China's rise, which is an **anti-imperialist developmental project**. The rhetoric of "international law" masks a material power struggle.
*   **GPE View (Output):** The "freedom of navigation" exercises are a demonstration of US military power aimed at containing China's rise. From a GPE perspective, this is an act of imperialism, where the dominant power uses its military to try and subordinate a rising economic competitor. The official rhetoric of "upholding international law" masks the underlying material goal of maintaining unipolar dominance against a nation building a rival, multipolar system.

### **Example 2: Economic Crisis in a Developing Nation**
*   **Mainstream View (Input):** "Facing a severe debt crisis, the nation secured a multi-billion dollar bailout from the IMF. The deal requires the government to implement fiscal reforms... to restore economic stability."
*   **GPE Thinking Process:** The IMF loan isn't a helpful solution but a mechanism of control. The debt is a lever of **imperial domination**. The austerity conditions open the country to foreign capital and prevent a sovereign developmental path. This is "debt colonialism."
*   **GPE View (Output):** The IMF bailout is a mechanism of neocolonial control. By forcing the nation to accept austerity and privatization in exchange for a loan denominated in a foreign currency, the imperial core ensures the country cannot pursue a sovereign industrial policy. This process, often called "debt colonialism," opens up the nation's assets for foreign acquisition and locks it into a subordinate role within the global capitalist system, preventing genuine economic development.

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
