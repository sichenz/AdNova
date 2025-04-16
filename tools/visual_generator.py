"""
Visual content generator for the Marketing Ad Agent.
This module handles the generation of images and videos using Stable Diffusion 3.5 and Mochi 1.
"""
import os
import time
import uuid
import subprocess
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

import torch
from config.settings import VISUAL_GENERATION_ENABLED, IMAGE_OUTPUT_DIR, VIDEO_OUTPUT_DIR

# Check if CUDA is available
CUDA_AVAILABLE = torch.cuda.is_available()

class VisualGenerator:
    """
    Generates visual content (images and videos) for marketing campaigns using
    Stable Diffusion 3.5 Large for images and Mochi 1 for videos.
    """
    
    def __init__(self, client):
        """
        Initialize the visual generator.
        
        Args:
            client: The OpenAI client (used for prompt enhancement)
        """
        self.client = client
        
        # Create output directories
        os.makedirs(IMAGE_OUTPUT_DIR, exist_ok=True)
        os.makedirs(VIDEO_OUTPUT_DIR, exist_ok=True)
        
        # Initialize models (lazy loading)
        self.sd_pipeline = None
        self.mochi_pipeline = None
        
        # Check if visual generation is enabled in settings
        self.is_enabled = VISUAL_GENERATION_ENABLED
        
        # Log initialization status
        if not self.is_enabled:
            print("Visual generation is disabled in settings. Only placeholder generation will be available.")
            return
        
        if not CUDA_AVAILABLE:
            print("Warning: CUDA is not available. Visual generation will be limited to CPU which may be very slow.")
    
    def generate_image(self, 
                     prompt: str, 
                     negative_prompt: str = "", 
                     width: int = 1024, 
                     height: int = 1024,
                     num_inference_steps: int = 28,
                     guidance_scale: float = 4.5,
                     seed: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate an image using Stable Diffusion 3.5 Large.
        
        Args:
            prompt: Text prompt for the image
            negative_prompt: Negative prompt (what not to include)
            width: Image width
            height: Image height
            num_inference_steps: Number of diffusion steps
            guidance_scale: Guidance scale for classifier-free guidance
            seed: Random seed for reproducibility
            
        Returns:
            Dictionary containing image metadata and path
        """
        enhanced_prompt = self._enhance_prompt_for_image(prompt)
        
        image_id = str(uuid.uuid4())
        output_path = os.path.join(IMAGE_OUTPUT_DIR, f"{image_id}.png")
        
        # Generate the image
        if self.is_enabled and CUDA_AVAILABLE:
            try:
                # Lazy load the pipeline
                if self.sd_pipeline is None:
                    try:
                        from diffusers import StableDiffusion3Pipeline
                        import torch
                        
                        print("Loading Stable Diffusion 3.5 Large model (this may take a moment)...")
                        self.sd_pipeline = StableDiffusion3Pipeline.from_pretrained(
                            "stabilityai/stable-diffusion-3.5-large", 
                            torch_dtype=torch.bfloat16
                        )
                        self.sd_pipeline = self.sd_pipeline.to("cuda")
                        
                        # To save memory
                        self.sd_pipeline.enable_vae_tiling()
                    except Exception as e:
                        print(f"Error loading Stable Diffusion model: {str(e)}")
                        self.sd_pipeline = None
                
                if self.sd_pipeline is not None:
                    # Set the seed if provided
                    generator = None
                    if seed is not None:
                        generator = torch.Generator("cuda").manual_seed(seed)
                    
                    # Generate the image
                    image = self.sd_pipeline(
                        prompt=enhanced_prompt,
                        negative_prompt=negative_prompt,
                        width=width,
                        height=height,
                        num_inference_steps=num_inference_steps,
                        guidance_scale=guidance_scale,
                        generator=generator
                    ).images[0]
                    
                    # Save the image
                    image.save(output_path)
                    real_generation = True
                else:
                    # Fallback to placeholder
                    self._generate_placeholder_image(output_path, width, height)
                    real_generation = False
            except Exception as e:
                print(f"Error generating image: {str(e)}")
                # Fallback to placeholder
                self._generate_placeholder_image(output_path, width, height)
                real_generation = False
        else:
            # Visual generation is disabled or CUDA is not available, generate placeholder
            self._generate_placeholder_image(output_path, width, height)
            real_generation = False
        
        # Create and return metadata
        metadata = {
            "image_id": image_id,
            "created_at": datetime.now().isoformat(),
            "prompt": prompt,
            "enhanced_prompt": enhanced_prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "seed": seed,
            "model": "Stable Diffusion 3.5 Large",
            "output_path": output_path,
            "real_generation": real_generation
        }
        
        return metadata
    
    def generate_video(self, 
                     prompt: str, 
                     negative_prompt: str = "", 
                     width: int = 848, 
                     height: int = 480,
                     num_frames: int = 31,
                     num_inference_steps: int = 50,
                     guidance_scale: float = 4.5,
                     seed: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate a video using Mochi 1.
        
        Args:
            prompt: Text prompt for the video
            negative_prompt: Negative prompt (what not to include)
            width: Video width
            height: Video height
            num_frames: Number of frames to generate
            num_inference_steps: Number of diffusion steps
            guidance_scale: Guidance scale for classifier-free guidance
            seed: Random seed for reproducibility
            
        Returns:
            Dictionary containing video metadata and path
        """
        enhanced_prompt = self._enhance_prompt_for_video(prompt)
        
        video_id = str(uuid.uuid4())
        output_path = os.path.join(VIDEO_OUTPUT_DIR, f"{video_id}.mp4")
        
        # Generate the video
        if self.is_enabled and CUDA_AVAILABLE:
            try:
                # Lazy load the pipeline
                if self.mochi_pipeline is None:
                    try:
                        from diffusers import MochiPipeline
                        import torch
                        
                        print("Loading Mochi 1 model (this may take a moment)...")
                        self.mochi_pipeline = MochiPipeline.from_pretrained(
                            "genmo/mochi-1-preview", 
                            variant="bf16", 
                            torch_dtype=torch.bfloat16
                        )
                        
                        # Enable memory savings
                        self.mochi_pipeline.enable_model_cpu_offload()
                        self.mochi_pipeline.enable_vae_tiling()
                    except Exception as e:
                        print(f"Error loading Mochi model: {str(e)}")
                        self.mochi_pipeline = None
                
                if self.mochi_pipeline is not None:
                    # Set the seed if provided
                    generator = None
                    if seed is not None:
                        generator = torch.Generator("cuda").manual_seed(seed)
                    
                    # Generate the video
                    with torch.autocast("cuda", torch.bfloat16, cache_enabled=False):
                        video = self.mochi_pipeline(
                            prompt=enhanced_prompt,
                            negative_prompt=negative_prompt,
                            width=width,
                            height=height,
                            num_frames=num_frames,
                            num_inference_steps=num_inference_steps,
                            guidance_scale=guidance_scale,
                            generator=generator
                        ).frames[0]
                    
                    # Export to video
                    from diffusers.utils import export_to_video
                    export_to_video(video, output_path, fps=30)
                    real_generation = True
                else:
                    # Fallback to placeholder
                    self._generate_placeholder_video(output_path, width, height, num_frames)
                    real_generation = False
            except Exception as e:
                print(f"Error generating video: {str(e)}")
                # Fallback to placeholder
                self._generate_placeholder_video(output_path, width, height, num_frames)
                real_generation = False
        else:
            # Visual generation is disabled or CUDA is not available, generate placeholder
            self._generate_placeholder_video(output_path, width, height, num_frames)
            real_generation = False
        
        # Create and return metadata
        metadata = {
            "video_id": video_id,
            "created_at": datetime.now().isoformat(),
            "prompt": prompt,
            "enhanced_prompt": enhanced_prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "num_frames": num_frames,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "seed": seed,
            "model": "Mochi 1",
            "output_path": output_path,
            "real_generation": real_generation
        }
        
        return metadata
    
    def generate_marketing_visuals(self, 
                                 campaign_brief: Dict[str, Any],
                                 content_type: str = "image", 
                                 count: int = 1,
                                 visual_theme: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Generate marketing visuals based on a campaign brief.
        
        Args:
            campaign_brief: The campaign brief
            content_type: Type of visual to generate ("image", "video", or "both")
            count: Number of visuals to generate of each type
            visual_theme: Optional theme to guide visual generation
            
        Returns:
            List of dictionaries containing visual metadata
        """
        # Extract relevant information from the campaign brief
        product_name = campaign_brief.get("product_name", "")
        description = campaign_brief.get("description", "")
        target_audience = campaign_brief.get("target_audience", "")
        campaign_goals = campaign_brief.get("campaign_goals", "")
        key_selling_points = campaign_brief.get("key_selling_points", [])
        tone = campaign_brief.get("tone", "professional")
        
        # Create base prompt from campaign brief
        base_prompt = f"Marketing {content_type} for '{product_name}'. {description}"
        
        # Add key selling points if available
        if key_selling_points:
            base_prompt += f" Highlighting key features: {', '.join(key_selling_points[:3])}"
        
        # Add tone information
        base_prompt += f" Using a {tone} tone."
        
        # Add visual theme if provided
        if visual_theme:
            base_prompt += f" Visual theme: {visual_theme}."
        
        # Generate visuals
        results = []
        
        # Set default sizes based on content type
        image_width, image_height = 1024, 1024  # Default square for general purpose
        video_width, video_height = 848, 480    # Default 16:9 aspect ratio
        
        # Adjust sizes based on content type if needed
        if "social_media" in campaign_brief.get("platform", "").lower():
            image_width, image_height = 1080, 1080  # Square for social
        
        for i in range(count):
            seed = int(time.time()) + i  # Different seed for each generation
            
            if content_type in ["image", "both"]:
                image_metadata = self.generate_image(
                    prompt=base_prompt,
                    width=image_width,
                    height=image_height,
                    seed=seed
                )
                results.append(image_metadata)
            
            if content_type in ["video", "both"]:
                video_metadata = self.generate_video(
                    prompt=base_prompt,
                    width=video_width,
                    height=video_height,
                    seed=seed
                )
                results.append(video_metadata)
        
        return results
    
    def _enhance_prompt_for_image(self, prompt: str) -> str:
        """
        Enhance a prompt for better image generation results.
        
        Args:
            prompt: Original prompt
            
        Returns:
            Enhanced prompt
        """
        try:
            enhancement_prompt = f"""
            I need to enhance this prompt for Stable Diffusion 3.5 Large image generation.
            Original prompt: "{prompt}"
            
            Please enhance this prompt with:
            1. More detailed visual descriptions
            2. Style and composition elements
            3. Lighting and atmosphere details
            4. Technical parameters if relevant (like high resolution, detailed, etc.)
            
            Return ONLY the enhanced prompt text with no additional explanation.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a prompt engineering expert for image generation models."},
                    {"role": "user", "content": enhancement_prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            enhanced_prompt = response.choices[0].message.content.strip()
            return enhanced_prompt
        except Exception as e:
            print(f"Error enhancing image prompt: {str(e)}")
            return prompt
    
    def _enhance_prompt_for_video(self, prompt: str) -> str:
        """
        Enhance a prompt for better video generation results.
        
        Args:
            prompt: Original prompt
            
        Returns:
            Enhanced prompt
        """
        try:
            enhancement_prompt = f"""
            I need to enhance this prompt for Mochi 1 video generation.
            Original prompt: "{prompt}"
            
            Please enhance this prompt with:
            1. More detailed visual descriptions
            2. Motion and action elements (what should be moving and how)
            3. Temporal progression details (what happens over time)
            4. Style, composition, and atmosphere elements
            5. Technical parameters if relevant (like high resolution, cinematic, etc.)
            
            Return ONLY the enhanced prompt text with no additional explanation.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a prompt engineering expert for video generation models."},
                    {"role": "user", "content": enhancement_prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            enhanced_prompt = response.choices[0].message.content.strip()
            return enhanced_prompt
        except Exception as e:
            print(f"Error enhancing video prompt: {str(e)}")
            return prompt
    
    def _generate_placeholder_image(self, output_path: str, width: int, height: int) -> None:
        """
        Generate a placeholder image when actual generation is not available.
        
        Args:
            output_path: Path to save the placeholder image
            width: Image width
            height: Image height
        """
        try:
            # Try to use PIL if available
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a new image with a gradient background
            image = Image.new("RGB", (width, height), color=(240, 240, 240))
            draw = ImageDraw.Draw(image)
            
            # Draw a placeholder rectangle
            draw.rectangle(
                [(width * 0.1, height * 0.1), (width * 0.9, height * 0.9)],
                outline=(200, 200, 200),
                width=5
            )
            
            # Draw text
            try:
                font = ImageFont.truetype("arial.ttf", size=int(height * 0.05))
            except:
                font = ImageFont.load_default()
            
            draw.text(
                (width // 2, height // 2),
                "Image Generation Placeholder\n(Stable Diffusion 3.5 Large)",
                fill=(100, 100, 100),
                font=font,
                anchor="mm",
                align="center"
            )
            
            # Save the image
            image.save(output_path)
        
        except Exception as e:
            print(f"Error generating placeholder image: {str(e)}")
            # Fallback to even simpler method if PIL fails
            with open(output_path, "w") as f:
                f.write("Placeholder image file")
    
    def _generate_placeholder_video(self, output_path: str, width: int, height: int, num_frames: int) -> None:
        """
        Generate a placeholder video when actual generation is not available.
        
        Args:
            output_path: Path to save the placeholder video
            width: Video width
            height: Video height
            num_frames: Number of frames
        """
        try:
            # Try to use FFMPEG if available
            import subprocess
            
            # Create a blank video with text
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi",
                "-i", f"color=c=gray:s={width}x{height}:d={num_frames/30}",
                "-vf", f"drawtext=text='Video Generation Placeholder (Mochi 1)':fontsize={height//10}:x=(w-text_w)/2:y=(h-text_h)/2:fontcolor=white",
                "-c:v", "libx264",
                "-t", f"{num_frames/30}",
                "-pix_fmt", "yuv420p",
                output_path
            ]
            
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        except Exception as e:
            print(f"Error generating placeholder video: {str(e)}")
            # Fallback to simple file creation if FFMPEG fails
            with open(output_path, "w") as f:
                f.write("Placeholder video file")