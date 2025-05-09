import { format, parseISO, isValid } from 'date-fns';
// Import for date-fns-tz version 3.x
import { formatInTimeZone } from 'date-fns-tz';

/**
 * Convert a UTC date string to local time
 * @param dateString ISO date string in UTC
 * @returns Date object in local timezone
 */
export function utcToLocal(dateString: string): Date {
  try {
    // For YYYY-MM-DD format dates, append time to create valid ISO
    if (dateString.length === 10 && dateString.includes('-')) {
      dateString = `${dateString}T00:00:00.000Z`;
    }
    
    // Parse the ISO string to a Date object
    const date = parseISO(dateString);
    
    if (!isValid(date)) {
      console.error(`Invalid date string: ${dateString}`);
      return new Date(); // Return current date as fallback
    }
    
    // Get user's timezone
    const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    
    try {
      // In date-fns-tz v3.x, utcToZonedTime was removed
      // Create a new Date with the offset from the user's timezone
      const isoInUserTz = formatInTimeZone(date, timeZone, "yyyy-MM-dd'T'HH:mm:ss.SSS");
      return new Date(isoInUserTz);
    } catch (tzError) {
      console.warn('date-fns-tz failed, using fallback method:', tzError);
      
      // Fallback: manual conversion using built-in JS Date methods
      const utcDate = new Date(dateString);
      // JavaScript's Date automatically handles local timezone when displaying
      return utcDate;
    }
  } catch (error) {
    console.error('Error in utcToLocal:', error);
    return new Date(); // Ultimate fallback
  }
}

/**
 * Format a UTC date string to local timezone using specified format
 * @param dateString ISO date string in UTC or YYYY-MM-DD format
 * @param formatString date-fns format string
 * @returns Formatted date string in local timezone
 */
export function formatLocalDate(dateString: string, formatString: string = 'PPP'): string {
  try {
    // Handle empty or null values
    if (!dateString) {
      return 'Invalid date';
    }
    
    const localDate = utcToLocal(dateString);
    
    if (!isValid(localDate)) {
      console.error(`Could not format date: ${dateString}`);
      return 'Invalid date';
    }
    
    return format(localDate, formatString);
  } catch (error) {
    console.error(`Error formatting date "${dateString}":`, error);
    // Fallback to simple formatting
    try {
      return format(parseISO(dateString), formatString);
    } catch (e) {
      return dateString || 'Invalid date';
    }
  }
}

/**
 * Create today's date in YYYY-MM-DD format in local timezone
 * @returns Today's date as YYYY-MM-DD in local timezone
 */
export function getTodayLocalDate(): string {
  const now = new Date();
  return format(now, 'yyyy-MM-dd');
}

/**
 * Compare if a date (in UTC) is in the future relative to local now
 * @param dateString ISO date string or YYYY-MM-DD in UTC
 * @returns boolean indicating if date is in the future
 */
export function isDateInFuture(dateString: string): boolean {
  try {
    const localDate = utcToLocal(dateString);
    const now = new Date();
    return localDate > now;
  } catch (error) {
    console.error(`Error checking if date "${dateString}" is in future:`, error);
    // Fallback to simple comparison if timezone conversion fails
    return parseISO(dateString) > new Date();
  }
}

/**
 * Convert a local Date object to UTC ISO string
 * @param localDate Local Date object
 * @returns ISO string in UTC
 */
export function localToUTC(localDate: Date): string {
  return localDate.toISOString();
} 