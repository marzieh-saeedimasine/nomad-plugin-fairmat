"""
Parser for sintering process CSV files.

Users can upload CSV files with the following columns:
- step name (or name): Name of the temperature ramp step
- duration [min]: Duration in minutes
- initial temperature [C]: Initial temperature in Celsius
- final temperature [C]: Final temperature in Celsius

Example CSV:
    step name,duration [min],initial temperature [C],final temperature [C]
    Heating,60,25,1000
    Soaking,120,1000,1000
    Cooling,180,1000,25
"""

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive

from nomad.parsing import MatchingParser
from nomad.units import ureg

from nomad_plugin_fairmat.schema_packages.sintering import (
    Sintering,
    TemperatureRamp,
)


class SinteringParser(MatchingParser):
    """
    Parser for sintering process CSV files.
    
    Reads CSV files with temperature ramp data and creates a Sintering entry
    with temperature ramp steps automatically parsed from the CSV.
    """

    def parse(
        self,
        mainfile: str,
        archive: 'EntryArchive',
        logger,
    ) -> None:
        """
        Parse sintering CSV file and populate the Sintering schema.
        
        Args:
            mainfile: Path to the CSV file
            archive: The entry archive to populate
            logger: Structlog logger
        """
        try:
            # Read the CSV file
            df = pd.read_csv(mainfile)
            
            # Create Sintering section
            sintering = Sintering()
            
            # Get filename as name
            sintering.name = mainfile.split('/')[-1].replace('.csv', '')
            
            # Parse each row as a TemperatureRamp step
            steps = []
            for _, row in df.iterrows():
                step = TemperatureRamp()
                
                # Try different column name variants
                step_name_col = None
                if 'step name' in row.index:
                    step_name_col = 'step name'
                elif 'name' in row.index:
                    step_name_col = 'name'
                elif 'Step Name' in row.index:
                    step_name_col = 'Step Name'
                
                if step_name_col:
                    step.name = str(row[step_name_col])
                
                # Duration - try different column variants
                for duration_col in ['duration [min]', 'duration[min]', 'Duration [min]', 'duration']:
                    if duration_col in row.index:
                        try:
                            step.duration = ureg.Quantity(float(row[duration_col]), 'minutes')
                        except (ValueError, TypeError):
                            logger.warning(f"Could not parse duration from {duration_col}: {row[duration_col]}")
                        break
                
                # Initial temperature - try different column variants
                for temp_col in ['initial temperature [C]', 'initial temperature[C]', 'Initial Temperature [C]', 'initial temperature', 'Initial Temp [C]']:
                    if temp_col in row.index:
                        try:
                            step.initial_temperature = ureg.Quantity(float(row[temp_col]), 'celsius')
                        except (ValueError, TypeError):
                            logger.warning(f"Could not parse initial temperature from {temp_col}: {row[temp_col]}")
                        break
                
                # Final temperature - try different column variants
                for temp_col in ['final temperature [C]', 'final temperature[C]', 'Final Temperature [C]', 'final temperature', 'Final Temp [C]']:
                    if temp_col in row.index:
                        try:
                            step.final_temperature = ureg.Quantity(float(row[temp_col]), 'celsius')
                        except (ValueError, TypeError):
                            logger.warning(f"Could not parse final temperature from {temp_col}: {row[temp_col]}")
                        break
                
                steps.append(step)
            
            sintering.steps = steps
            archive.data = sintering
            
            logger.info(f"Successfully parsed sintering CSV with {len(steps)} temperature ramp steps")
            
        except Exception as e:
            logger.error(f"Error parsing sintering CSV file: {str(e)}")
            # Still create an empty Sintering section for the archive
            archive.data = Sintering()
