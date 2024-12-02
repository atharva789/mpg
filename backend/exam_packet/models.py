# exam_packet/models.py

import os
import fitz  # PyMuPDF for PDF processing
import io
import torch
from transformers import (
    LayoutLMv3Processor,
    LayoutLMv3ForTokenClassification,
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
)
from transformers.pipelines import pipeline
from PIL import Image
import nltk
nltk.download('all', quiet=True)

from nltk.tokenize import sent_tokenize

# Download NLTK data files (only needed once)

from django.db import models
from django.contrib.auth.models import User
from assessment.models import Assessment
from resources.models import Resource
from django.core.files.base import ContentFile
from django.conf import settings


class Packet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    assessment = models.OneToOneField(Assessment, on_delete=models.CASCADE, related_name="exam_packet")
    # title = models.CharField(max_length=255)
    pdf_file = models.FileField(upload_to="packets/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Packet for {self.assessment.title}"

    def save(self, *args, **kwargs):
        # Save the instance first to get an ID
        super().save(*args, **kwargs)

        if not self.pdf_file:
            # Step 1: Retrieve the syllabus and course materials paths
            resource_query = Resource.objects.filter(user=self.user, assessment=self.assessment)
            syllabus_path = None
            material_paths = []

            for resource in resource_query:
                if resource.resource_type == "syllabus":
                    syllabus_path = resource.resource_pdf_file.path
                else:
                    material_paths.append(resource.resource_pdf_file.path)

            if not syllabus_path:
                raise Exception("Syllabus not found for the assessment.")

            # Step 2: Read requirements from ExamPacketRequirements.txt
            requirements_path = os.path.join(settings.BASE_DIR, 'ExamPacketRequirements.txt')
            with open(requirements_path, 'r') as file:
                requirements_text = file.read()

            # Step 3: Generate the exam packet
            generator = PacketGenerator(syllabus_path, material_paths)
            pdf_buffer = generator.generate_packet(requirements_text)

            # Step 4: Save the PDF to the pdf_file field
            pdf_file_name = f"{self.title.replace(' ', '_')}.pdf"
            self.pdf_file.save(pdf_file_name, ContentFile(pdf_buffer.read()))
            self.save()

class PacketGenerator:
    def __init__(self, syllabus_pdf_path, material_pdf_paths):
        """
        Initializes the PacketGenerator with a syllabus and course materials.

        :param syllabus_pdf_path: Path to the syllabus PDF file.
        :param material_pdf_paths: List of paths to course material PDF files.
        """
        self.syllabus_pdf_path = syllabus_pdf_path
        self.material_pdf_paths = material_pdf_paths

        # Initialize models and processors
        self.layout_processor = LayoutLMv3Processor.from_pretrained(
            'microsoft/layoutlmv3-base', apply_ocr=False
        )
        self.layout_model = LayoutLMv3ForTokenClassification.from_pretrained(
            'microsoft/layoutlmv3-base', num_labels=10
        )
        self.summarizer = pipeline("summarization", model="t5-base", tokenizer="t5-base")

    def read_syllabus(self):
        """
        Reads the syllabus PDF and extracts relevant topics.
        """
        syllabus_text = self.extract_text_from_pdf(self.syllabus_pdf_path)
        topics = self.extract_topics_from_text(syllabus_text)
        return topics

    def extract_text_from_pdf(self, pdf_path):
        """
        Extracts text from a PDF file using PyMuPDF.
        """
        doc = fitz.open(pdf_path)
        full_text = ""
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            full_text += text + "\n"
        doc.close()
        return full_text

    def extract_topics_from_text(self, text):
        """
        Extracts topics from text using keyword extraction.
        """
        # Using NLTK for topic extraction
        words = nltk.word_tokenize(text)
        words = [word.lower() for word in words if word.isalpha()]
        freq_dist = nltk.FreqDist(words)
        common_words = freq_dist.most_common(20)
        topic_list = [word for word, freq in common_words]
        return topic_list

    def process_course_materials(self):
        """
        Processes course material PDFs to extract relevant information.
        """
        extracted_info = []
        for pdf_path in self.material_pdf_paths:
            page_count = self.get_pdf_page_count(pdf_path)
            if page_count > 50:
                # For long documents, extract text directly
                text = self.extract_text_from_pdf(pdf_path)
            else:
                # Use LayoutLMv3 for documents with complex layouts
                text = self.extract_text_with_layoutlmv3(pdf_path)
            extracted_info.append(text)
        return extracted_info

    def extract_text_with_layoutlmv3(self, pdf_path):
        """
        Extracts text from PDF using LayoutLMv3 for better layout understanding.
        """
        doc = fitz.open(pdf_path)
        full_text = ""
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_width, page_height = page.rect.width, page.rect.height

            # Extract words and bounding boxes
            words_on_page = page.get_text("words")
            words = [w[4] for w in words_on_page]
            bboxes = [self.normalize_bbox(w[:4], page_width, page_height) for w in words_on_page]

            # Get the page image
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Prepare inputs for the model
            encoding = self.layout_processor(
                img, words, boxes=bboxes, return_tensors="pt",
                truncation=True, padding="max_length"
            )

            # Run through the model
            outputs = self.layout_model(**encoding)
            logits = outputs.logits
            predictions = torch.argmax(logits, dim=2)
            predicted_labels = [self.layout_model.config.id2label[p.item()] for p in predictions[0]]

            # Combine words into text
            page_text = ' '.join(words)
            full_text += page_text + "\n"

        doc.close()
        return full_text

    def normalize_bbox(self, bbox, page_width, page_height):
        x0, y0, x1, y1 = bbox
        return [
            int(1000 * x0 / page_width),
            int(1000 * y0 / page_height),
            int(1000 * x1 / page_width),
            int(1000 * y1 / page_height),
        ]

    def get_pdf_page_count(self, pdf_path):
        try:
            with fitz.open(pdf_path) as doc:
                return len(doc)
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return 0

    def generate_packet_content(self, syllabus_topics, materials_texts, requirements_text):
        """
        Generates the exam packet content based on extracted topics and materials.
        """
        # Combine all texts
        combined_text = '\n'.join(materials_texts)

        # Summarize the combined text to align with syllabus topics
        summarized_sections = {}
        for topic in syllabus_topics:
            # Extract relevant sentences containing the topic
            topic_sentences = [
                sent for sent in sent_tokenize(combined_text)
                if topic.lower() in sent.lower()
            ]
            topic_text = ' '.join(topic_sentences)
            # Summarize the topic text
            if topic_text:
                try:
                    summary = self.summarizer(
                        topic_text, max_length=150, min_length=40, do_sample=False
                    )[0]['summary_text']
                except Exception as e:
                    print(f"Summarization error for topic '{topic}': {e}")
                    summary = topic_text[:500]  # Fallback to first 500 characters
                summarized_sections[topic] = summary

        # Incorporate requirements from the text file
        packet_content = self.apply_requirements(summarized_sections, requirements_text)
        return packet_content

    def apply_requirements(self, summarized_sections, requirements_text):
        """
        Structures the packet content according to the requirements.
        """
        packet_content = requirements_text + "\n\n"

        for topic, summary in summarized_sections.items():
            packet_content += f"## {topic.capitalize()}\n\n{summary}\n\n"
        return packet_content

    def generate_packet_pdf(self, packet_content):
        """
        Generates a PDF file from the packet content.
        """
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        from io import BytesIO

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Split content into lines for rendering
        lines = packet_content.split('\n')
        text_object = p.beginText()
        text_object.setTextOrigin(inch, height - inch)
        text_object.setFont("Helvetica", 12)

        for line in lines:
            if text_object.getY() <= inch:
                p.drawText(text_object)
                p.showPage()
                text_object = p.beginText()
                text_object.setTextOrigin(inch, height - inch)
                text_object.setFont("Helvetica", 12)
            text_object.textLine(line)

        p.drawText(text_object)
        p.save()

        buffer.seek(0)
        return buffer

    def generate_packet(self, requirements_text):
        """
        Main method to generate the exam packet.

        :param requirements_text: Text from ExamPacketRequirements.txt to guide packet generation.
        :return: BytesIO object containing the PDF data.
        """
        # Step 1: Read and process the syllabus
        syllabus_topics = self.read_syllabus()

        # Step 2: Process course material PDFs
        materials_texts = self.process_course_materials()

        # Step 3: Generate the packet content
        packet_content = self.generate_packet_content(
            syllabus_topics, materials_texts, requirements_text
        )

        # Step 4: Generate PDF from packet content
        pdf_buffer = self.generate_packet_pdf(packet_content)

        return pdf_buffer