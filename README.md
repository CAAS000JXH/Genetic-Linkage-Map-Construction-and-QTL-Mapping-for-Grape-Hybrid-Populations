1 Parent Heterozygosity Analysis Workflow
# Using the maternal parent as an example, perform a reverse complement of zhuosexiang_2.fasta
$ seqkit seq zhuosexiang_2.fasta -r -p > zhuosexiang_2_re.fasta
# Merge paired-end sequencing data.
$ cat zhuosexiang_1.fasta zhuosexiang_2_re.fasta > total.fasta
# Calculate k-mer
$ jellyfish count -C -m 21 -s 4G -t 8 total.fasta -o kmer21.out
$ jellyfish histo kmer21.out -o kmer21.histo
# Calculate the heterozygosity of the genome
$ genomescope.R -i kmer21.histo -o zsx -p 2 -k 21

2 Reads_to_VCF Analysis Pipeline
# Step 1: Quality control of sequencing data.
$ fastp -i ${sample}_1.fq.gz -o ${sample}_1.clean.fq.gz -I ${sample}_2.fq.gz -O ${sample}_2.clean.fq.gz -h ${sample}.html -j ${sample}.json 2> ${sample}.txt

# Step 2: Build a reference genome index.
$ mkdir ref
$ bwa index ref/hap1.genome.T2T.fasta
$ samtools faidx ref/hap1.genome.T2T.fasta

# Step 3: Align reads to the reference genome.
$ bwa mem -t 80 -R "@RG\tID:${i}\tPL:illumina\tSM:${i}"  ref/hap1.genome.T2T.fasta ./fastp/${i}_1.clean.fq.gz  ./fastp/${i}_2.clean.fq.gz | samtools view -Sb - > bam_hap1/${i}.bam

# Step 4: Sort the BAM files by chromosome position.
$ samtools sort -@ 40 -m 4G -O bam -o ${i}.sort.bam ${i}.bam

# Step 5: Remove PCR duplicates.
$ gatk MarkDuplicates -I ${i}.sort.bam -O ${i}.rmdup.bam -M ${i}.sorted.markdup_metrics.txt

# Step 6: Add index tags.
$ samtools index ${i}.rmdup.bam

# Step 7: Generate GVCF files.
gatk HaplotypeCaller -R ref/hap1.genome.T2T.fasta \
    --emit-ref-confidence GVCF \
    -I ${i}.rmdup.bam \
    -stand-call-conf 30 --sample-ploidy 2 \
    -O ${i}.g.vcf 

# Step 8: Merge the offspring GVCF files and extract SNP variant information.
$ gatk CombineGVCFs -R ref/hap1.genome.T2T.fasta --variant gvcf.list -O offspring.g.vcf 
$ gatk GenotypeGVCFs -R ref/hap1.genome.T2T.fasta -V offspring.g.vcf -O offspring.vcf
$ gatk SelectVariants -R ref/hap1.genome.T2T.fasta -V offspring.vcf -select-type SNP  -O offspring.SNP.vcf 

# Step 9: Merge the parent GVCF files and extract SNP variant information.
$ gatk CombineGVCFs -R ref/hap1.genome.T2T.fasta --variant heicuiwuhe.g.vcf --variant zhuosexiang.g.vcf -O parent.g.vcf 
$ gatk GenotypeGVCFs -R ref/hap1.genome.T2T.fasta -V parent.g.vcf -O parent.vcf
$ gatk SelectVariants -R ref/hap1.genome.T2T.fasta -V parent.vcf -select-type SNP  -O parent.SNP.vcf 

3 VCF_to_binMap Analysis Pipeline
This analysis pipeline script is primarily developed using Python 3.10. The required dependencies are: pysam, openpyxl, pandas, numpy, and scipy.

# Filter and convert the input VCF file. Please note the order of the parents in the VCF file; the female must be listed first, followed by the male. The minimum coverage for parent variant sites and the minimum coverage for offspring variant sites should be set according to actual requirements. For example, the minimum coverage for parent variant sites is set to 6, and the minimum coverage for offspring variant sites is set to 3.
$ python parents_vcf_filter.py ${input_parent_vcf_file} filtered.parents.vcf ${female_ID} ${male_ID} ${minimum_coverage_for_parent_variants}
$ python offsprings_vcf_filter.py ${input_offspring_vcf_file} filtered.offsprings.vcf ${minimum_coverage_for_offspring_variants}
# VCF files are large and slow to process; only useful information should be extracted and saved as a CSV file to improve downstream computational efficiency.
$ bcftools query -f '%CHROM;%POS;%REF;%ALT[;%GT]\n' filtered.parents.vcf > filtered.parents.csv
$ bcftools query -f '%CHROM;%POS;%REF;%ALT[;%GT]\n' filtered.offsprings.vcf > filtered.offsprings.csv
# Extract sample IDs from the VCF file.
$ bcftools query -l filtered.offsprings.vcf > samples_header.txt
# Merge the variant sites of parents and offspring.
$ awk -F ';' 'BEGIN {OFS = FS} NR==FNR {a[$1","$2]=$1 FS $2 FS $3 FS $4 FS $5 FS $6; next} ($1","$2 in a) {line=a[$1","$2]; for(i=5; i<=NF; i++) line=line OFS $i; print line}' filtered.parents.csv filtered.offsprings.csv > merged.variant.csv
# Filter out variant sites in the offspring with excessive missing data; for example, with 198 offspring, you can set the threshold for missing data to 50.
$ python filtered.merged.variant.py merged.variant.csv filtered.merged.variant.csv ${missing_threshold}
# Filter the data based on parent types, requiring that the ${parent_selection} can only be male or female.
$ python filter_by_parent_type.py filtered.merged.variant.csv ${parent_selection}
# Split the data files by chromosome ID.
$ bcftools query -f '%CHROM\n' filtered.parents.vcf | sort -u > chromosome_ids.txt
$ python split_chromosome_files.py ${parent_selection}
# Construct MNP molecular markers.
$ python MNP_marker_building.py ${parent_selection} chromosome_ids.txt
# Determine the genotypes of the offspring MNP markers.
$ python MNP_maker_genotype.py chromosome_ids.txt ${parent_selection} ${progeny_count}
# Filter the genotype data of the offspring MNP markers, requiring that the missing rate of sites does not exceed 25%. Perform a chi-squared test and only output sites with p > 0.05.
$ python MNP_maker_filter.py chromosome_ids.txt ${parent_selection} ${progeny_count}
# Check each line of the MNP markers to see if a swap is needed. For example, replace nn with np and np with nn.
$ python MNP_maker_swap.py chromosome_ids.txt ${parent_selection} 
# Determine the segregation types of bins based on MNP genotypes.
$ python bin_maker_genotype.py chromosome_ids.txt ${parent_selection} ${bin_window_size}
# Correct the genotypes of the bins.
$ python bin_correct_genotypes.py chromosome_ids.txt ${parent_selection} 
# Output the results.
$ python output_to_xlsx.py chromosome_ids.txt ${parent_selection}  ${output_file} samples_header.txt 
