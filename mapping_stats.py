import argparse
import subprocess

# Get depth
def get_mean_depth(bamfile, threads):
    """Calculate mean depth using samtools"""
    depth_command = f"samtools depth -a -@ {threads} {bamfile}"
    depth_process = subprocess.Popen(depth_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = depth_process.communicate()

    if depth_process.returncode != 0:
        raise Exception(f"Error calculating depth for {bamfile}: {stderr.decode('utf-8')}")
    
    depths = [int(line.split()[2]) for line in stdout.decode('utf-8').splitlines()]
    mean_depth = sum(depths) / len(depths) if depths else 0
    return mean_depth

# Get mapping proportion to reference
def get_proportion_mapped(bamfile, threads):
    """Calculate proportion of reads mapped to reference genome"""
    flagstat_command = f"samtools flagstat -@ {threads} {bamfile}"
    flagstat_process = subprocess.Popen(flagstat_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = flagstat_process.communicate()

    if flagstat_process.returncode != 0:
        raise Exception(f"Error calculating proportion for {bamfile}: {stderr.decode('utf-8')}")
    
    for line in stdout.decode('utf-8').splitlines():
        if "mapped (" in line:
            proportion = line.split()[4].strip("()%")
            return proportion
    return 0

def process_bam_files(input, output, threads):
    """Process BAM files and output results to file."""
    with open(input, 'r') as infile:
        bam_files = [line.strip() for line in infile]

    with open(output, 'w') as outfile:
        # Write headers
        outfile.write("File\tMean_depth\tPercentage_of_mapped_reads\n")

        for bamfile in bam_files:
            try:
                mean_depth = get_mean_depth(bamfile, threads)
                proportion_mapped = get_proportion_mapped(bamfile, threads)

                # Write results to output
                outfile.write(f"{bamfile}\t{mean_depth}\t{proportion_mapped}\n")
            except Exception as e:
                print(f"Error processsing {bamfile}: {e}")

def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description='Bulk calculate mean depth and proportion of mapped reads for BAM files')
    parser.add_argument('-i', '--input', required=True, help='Input file containing a list of BAM files')
    parser.add_argument('-o', '--output', required=True, help='Output filename')
    parser.add_argument('-t', '--threads', type=int, default=2, help='Number of threads for samtools (default: 2)')

    args = parser.parse_args()

    process_bam_files(args.input, args.output, args.threads)

if __name__ == "__main__":
    main()