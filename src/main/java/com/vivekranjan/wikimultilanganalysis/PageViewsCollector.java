/**
 * 
 */
package com.vivekranjan.wikimultilanganalysis;

import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.Reader;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.StringTokenizer;

import org.apache.commons.cli.BasicParser;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.apache.commons.csv.CSVRecord;
import org.joda.time.DateTime;
import org.joda.time.format.DateTimeFormat;
import org.joda.time.format.DateTimeFormatter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.wikibrain.conf.ConfigurationException;
import org.wikibrain.core.cmd.Env;
import org.wikibrain.core.cmd.EnvBuilder;
import org.wikibrain.core.dao.DaoException;
import org.wikibrain.core.lang.Language;
import org.wikibrain.core.lang.LanguageSet;
import org.wikibrain.pageview.PageViewDao;

import edu.emory.mathcs.backport.java.util.Arrays;

/**
 * Reads data about Wiki pages from a file and get their page view data for an
 * interval of time and write to an output file.
 * 
 * @author Vivek Ranjan
 *
 */
public class PageViewsCollector {

	private static final Logger logger = LoggerFactory
			.getLogger(PageViewsCollector.class);
	private static final String INPUT_FILE_PREFIX = "categories-full-";

	private static final String OUTPUT_FILE_PREFIX = "pageviews-count-";

	private static final String TSV_EXTENSION = ".tsv";

	private static final String CONF_WIKIBRAIN_OPTION = "c";

	private static final String END_DATE_OPTION = "ed";
	private static final String START_DATE_OPTION = "sd";
	private static final String INPUT_FILE_PATH_OPTION = "if";
	private static final String OUTPUT_FILE_PATH_OPTION = "of";
	private static final String WIKI_LANG_OPTION = "langs";
	private static String inputDirectoryPath;
	private static String outputDirectoryPath;
	private static DateTime startDate;
	private static DateTime endDate;
	private static String langCodes;

	/**
	 * @param args
	 * @throws ConfigurationException
	 * @throws ParseException
	 */
	public static void main(String[] args) throws ConfigurationException,
			ParseException {

		DateTimeFormatter dateTimeFormat = DateTimeFormat
				.forPattern("yyyy-MM-dd HH:mm:ss");
		DateTimeFormatter dateFormat = DateTimeFormat.forPattern("yyyy-MM-dd");

		Options options = new Options();
		options.addOption(INPUT_FILE_PATH_OPTION, true,
				"Complete path of the folder containing all the input files.");
		options.addOption(OUTPUT_FILE_PATH_OPTION, true,
				"Complete path of the input file.");
		options.addOption(START_DATE_OPTION, true, "Start date");
		options.addOption(END_DATE_OPTION, true, "End date");
		options.addOption(WIKI_LANG_OPTION, true,
				"Language code for the wikipedia to use.");
		options.addOption(CONF_WIKIBRAIN_OPTION, true,
				"customized conf file used by wikibrain");

		CommandLineParser parser = new BasicParser();
		CommandLine cmd = parser.parse(options, args);
		if (cmd.hasOption(INPUT_FILE_PATH_OPTION)) {
			inputDirectoryPath = cmd.getOptionValue(INPUT_FILE_PATH_OPTION);
		}
		if (cmd.hasOption(START_DATE_OPTION)) {
			startDate = dateTimeFormat.parseDateTime(cmd
					.getOptionValue(START_DATE_OPTION));
		}
		if (cmd.hasOption(END_DATE_OPTION)) {
			endDate = dateTimeFormat.parseDateTime(cmd
					.getOptionValue(END_DATE_OPTION));
		}
		if (cmd.hasOption(WIKI_LANG_OPTION)) {
			langCodes = cmd.getOptionValue(WIKI_LANG_OPTION);
		}
		if (cmd.hasOption(OUTPUT_FILE_PATH_OPTION)) {
			outputDirectoryPath = cmd.getOptionValue(OUTPUT_FILE_PATH_OPTION);
		}

		String argsForWikiBrain[] = new String[1];
		if (cmd.hasOption(CONF_WIKIBRAIN_OPTION)) {
			argsForWikiBrain[0] = cmd.getOptionValue(CONF_WIKIBRAIN_OPTION);
		}

		// Configure environment
		Env env = EnvBuilder.envFromArgs(argsForWikiBrain);
		final PageViewDao viewDao = env.getConfigurator()
				.get(PageViewDao.class);
		List<String> langs = new ArrayList<String>();
		if (langCodes.contains(",")) {
			StringTokenizer langTokenizer = new StringTokenizer(langCodes, ",");
			while (langTokenizer.hasMoreTokens()) {
				String currentLang = langTokenizer.nextToken();
				langs.add(currentLang);
				logger.info("Adding language: " + currentLang);
			}
		} else {
			// Only one langCode was provided
			langs.add(langCodes);
			logger.info("Adding language: " + langCodes);
		}
		DateTime startDateTime = new DateTime(startDate);
		DateTime endDateTime = new DateTime(endDate);
		LanguageSet languages = null;
		try {
			languages = new LanguageSet(langCodes);
			logger.info("Ensuring pageview information has been loaded.");
			viewDao.ensureLoaded(startDateTime, endDateTime, languages);
		} catch (DaoException e1) {
			e1.printStackTrace();
		}

		// Process languages
		for (String lang : langs) {
			Language language = Language.getByLangCode(lang);
			String inputFilePath = inputDirectoryPath + "/" + INPUT_FILE_PREFIX
					+ lang + TSV_EXTENSION;
			logger.info("Processing language: " + lang);
			logger.info("Using input file: " + inputFilePath);
			String outputFilePath = outputDirectoryPath + "/"
					+ OUTPUT_FILE_PREFIX + lang + TSV_EXTENSION;
			logger.info("Using output file: " + outputFilePath);
			int i = 0;
			try {
				Reader in = new FileReader(inputFilePath);
				Iterable<CSVRecord> records = CSVFormat.TDF.parse(in);
				List<String[]> outputs = new ArrayList<String[]>();
				Iterator<CSVRecord> iterator = null;
				try {
					iterator = records.iterator();
				} catch (Exception e3) {
					logger.error(
							"Problem parsing records, going to next language.",
							e3);
					continue;
				}
				boolean hasNext = false;
				try {
					hasNext = iterator.hasNext();
				} catch (Exception e3) {
					e3.printStackTrace();
					logger.error("Unable to get record.", e3);
				}
				while (hasNext) {
					CSVRecord record = null;
					try {
						record = iterator.next();
					} catch (Exception e2) {
						logger.error("Problem parsing record no." + i, e2);
						continue;
					}
					Integer pageId = null;
					try {
						pageId = Integer.parseInt(record.get(1));
					} catch (NumberFormatException e1) {
						logger.error("Problem parsing pageId for record no."
								+ i, e1);
						try {
							hasNext = iterator.hasNext();
						} catch (Exception e3) {
							e3.printStackTrace();
							logger.error("Unable to get record.", e3);
						}
						continue;
					}
					String category = "";
					try {
						category = record.get(0);
					} catch (Exception e1) {
						logger.error("Problem parsing category for record no."
								+ i, e1);
						category = "N/A";
					}
					try {
						for (DateTime date = startDate; date.isBefore(endDate); date = date
								.plusDays(1)) {
							DateTime plus = date.plus(86399000);
							Integer numViews = viewDao.getNumViews(language,
									pageId, startDateTime, plus);
							String[] row = new String[4];
							row[0] = pageId.toString();
							row[1] = dateFormat.print(date);
							row[2] = numViews.toString();
							row[3] = category;
							outputs.add(row);
						}
					} catch (NumberFormatException e) {
						e.printStackTrace();
					} catch (DaoException e) {
						e.printStackTrace();
					}
					i++;
					try {
						hasNext = iterator.hasNext();
					} catch (Exception e3) {
						e3.printStackTrace();
						logger.error("Unable to get record no." + i, e3);
						try {
							record = iterator.next();
						} catch (Exception e2) {
							logger.error("Problem parsing record no." + i, e2);
							continue;
						}
					}
				}
				Appendable outputFile = new FileWriter(outputFilePath);
				logger.info("Writing output file.");
				CSVPrinter print = CSVFormat.TDF.print(outputFile);
				for (String[] output : outputs) {
					print.printRecord(Arrays.asList(output));
				}
			} catch (IOException e) {
				e.printStackTrace();
			}
		}

	}

}
