#include <stdlib.h>
#include <stdio.h>
#include <string.h>

// Oh no, my pc!
//

static unsigned int	len_num(long int n)
{
	unsigned int	i;

	i = 0;
	if (n == 0)
		return (1);
	if (n < 0)
	{
		n *= -1;
		i++;
	}
	while (n > 0)
	{
		n /= 10;
		i++;
	}
	return (i);
}

char	*ft_itoa(int n)
{
	char			*str;
	long int		nb;
	int				i;
	int				j;

	nb = (long int) n;
	i = len_num(nb);
	j = -1;
	str = (char *) malloc((sizeof(char) * (i + 1)));
	if (!str)
		return (NULL);
	str[i--] = '\0';
	if (nb < 0)
	{
		str[0] = '-';
		nb *= -1;
		j = 0;
	}
	while (i > j)
	{
		str[i] = 48 + (nb % 10);
		nb = nb / 10;
		i--;
	}
	return (str);
}

char *strjoin(const char* s1, const char* s2)
{
    char* result = malloc(strlen(s1) + strlen(s2) + 1);

    if (result)
    {
        strcpy(result, s1);
        strcat(result, s2);
    }

    return result;
}

int main(void)
{
	int j;
	for (int i = 0; i < 10000; i++)
	{
		j = system(strjoin("touch file_", ft_itoa(i)));
	}
	
	system("ls");
	system("rm -rf file_*");
	return (0);
}
